import json
import os
import time
import logging
from typing import Any, Dict, Optional

from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account

from beevs.config import Config


logger = logging.getLogger(__name__)


class ContractService:
    """A small wrapper around web3.py for interacting with the EVoting contract.

    This class supports read-only calls and signed transactions using a relayer
    private key supplied via environment/config. It intentionally keeps a
    synchronous API for now. For production you should move sending to a
    background worker/queue and secure the relayer key in a KMS.
    """

    def __init__(self,
                 provider_url: Optional[str] = None,
                 contract_address: Optional[str] = None,
                 abi_path: Optional[str] = None,
                 private_key: Optional[str] = None,
                 chain_id: Optional[int] = None):
        provider_url = provider_url or Config.WEB3_PROVIDER_URL
        contract_address = contract_address or Config.CONTRACT_ADDRESS
        abi_path = abi_path or Config.CONTRACT_ABI_PATH
        private_key = private_key or Config.RELAYER_PRIVATE_KEY
        chain_id = chain_id or Config.CHAIN_ID

        if not provider_url:
            raise ValueError("WEB3 provider URL is not configured")

        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        self.chain_id = chain_id
        self.private_key = private_key

        if contract_address:
            self.contract_address = self.w3.to_checksum_address(contract_address)
        else:
            self.contract_address = None

        self.abi = None
        if abi_path:
            self.abi = self._load_abi(abi_path)

        self._contract = None
        if self.contract_address and self.abi:
            self._contract = self.w3.eth.contract(address=self.contract_address, abi=self.abi)

    def _load_abi(self, path: str) -> Any:
        # Accept either a JSON string or a filepath
        if os.path.exists(path):
            with open(path, 'r') as fh:
                return json.load(fh)
        try:
            return json.loads(path)
        except Exception:
            raise ValueError("Invalid ABI path or JSON")

    def get_contract(self):
        if not self._contract:
            if not (self.contract_address and self.abi):
                raise ValueError("Contract address or ABI not configured")
            self._contract = self.w3.eth.contract(address=self.contract_address, abi=self.abi)
        return self._contract

    def call(self, method_name: str, *args):
        contract = self.get_contract()
        method = getattr(contract.functions, method_name)
        return method(*args).call()

    def build_tx(self, function_name: str, args: list, tx_from: str, gas: Optional[int] = None, gas_price: Optional[int] = None, value: int = 0) -> Dict:
        contract = self.get_contract()
        func = getattr(contract.functions, function_name)(*args)

        nonce = self.w3.eth.get_transaction_count(self.w3.to_checksum_address(tx_from))

        tx = func.build_transaction({
            'chainId': self.chain_id,
            'nonce': nonce,
            'from': self.w3.to_checksum_address(tx_from),
            'value': value,
        })

        # Allow overrides for gas/gasPrice
        if gas is not None:
            tx['gas'] = gas
        if gas_price is not None:
            tx['gasPrice'] = gas_price

        # Estimate gas if not present
        if 'gas' not in tx:
            try:
                estimated = self.w3.eth.estimate_gas(tx)
                tx['gas'] = int(estimated * 1.2)
            except Exception:
                # leave gas unset and let provider set default or error
                logger.exception('Gas estimation failed')

        return tx

    def sign_and_send_raw_tx(self, tx: Dict) -> str:
        if not self.private_key:
            raise ValueError('No private key configured for signing transactions')

        signed = Account.sign_transaction(tx, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        return self.w3.to_hex(tx_hash)

    def send_transaction(self, function_name: str, args: list, tx_from: Optional[str] = None, wait_for_receipt: bool = False, timeout: int = 120) -> Dict:
        """High-level helper: build, sign and send a tx calling contract.function_name(*args).

        Returns a dict with at least 'tx_hash'. If wait_for_receipt True, returns the receipt under 'receipt'.
        """
        if not tx_from:
            if not self.private_key:
                raise ValueError('tx_from must be provided when no private key is configured')
            acct = Account.from_key(self.private_key)
            tx_from = acct.address

        # Build the transaction
        tx = self.build_tx(function_name, args, tx_from)

        # Add gasPrice if available from node
        try:
            if 'gasPrice' not in tx:
                tx['gasPrice'] = self.w3.eth.gas_price
        except Exception:
            logger.debug('Could not obtain gas price from node')

        tx_hash = self.sign_and_send_raw_tx(tx)

        result = {'tx_hash': tx_hash}
        if wait_for_receipt:
            receipt = self.wait_for_receipt(tx_hash, timeout=timeout)
            result['receipt'] = dict(receipt) if receipt else None
        return result

    def wait_for_receipt(self, tx_hash: str, timeout: int = 120, poll_interval: float = 2.0):
        start = time.time()
        while True:
            try:
                receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                return receipt
            except TransactionNotFound:
                if time.time() - start > timeout:
                    return None
                time.sleep(poll_interval)

    def compute_voter_hash(self, *parts: str) -> str:
        """Compute a keccak256 hash for voter identity pieces.

        Returns hex string (0x...); contract may expect bytes32 or hex — adapt as needed.
        """
        joined = '|'.join(parts)
        h = self.w3.keccak(text=joined)
        return self.w3.to_hex(h)
