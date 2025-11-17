import json
import os
import time
from typing import Any, Dict, Optional, Sequence

from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account

from beevs.config import Config


class ContractService:
    """ContractService encapsulates web3.py interactions for EVoting.

    Principles implemented:
    - Fail fast on misconfiguration (missing provider/ABI/chain mismatch).
    - Use node-detected chain id and require it to match configured CHAIN_ID when provided.
    - Use EIP-1559 fee fields when the node supports them; fallback to legacy gasPrice.
    - Do not swallow exceptions; let callers observe failures and handle them.
    """

    def __init__(
        self,
        provider_url: Optional[str] = None,
        contract_address: Optional[str] = None,
        abi_path: Optional[str] = None,
        private_key: Optional[str] = None,
        chain_id: Optional[int] = None,
    ) -> None:
        provider_url = provider_url or Config.WEB3_PROVIDER_URL
        contract_address = contract_address or Config.CONTRACT_ADDRESS
        abi_path = abi_path or Config.CONTRACT_ABI_PATH
        private_key = private_key or Config.RELAYER_PRIVATE_KEY
        configured_chain = chain_id or Config.CHAIN_ID

        if not provider_url:
            raise RuntimeError("WEB3 provider URL is not configured")

        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        if not self.w3.is_connected():
            raise RuntimeError(f"Unable to connect to WEB3 provider at {provider_url}")

        # Determine chain id from node
        node_chain_id = None
        try:
            node_chain_id = int(self.w3.eth.chain_id)
        except Exception:
            # If we cannot determine chain id, leave as None and allow configured_chain
            node_chain_id = None

        if configured_chain is not None:
            try:
                configured_chain = int(configured_chain)
            except Exception:
                configured_chain = None

        # If both are present and differ, raise - explicit failure is better than silent mismatch
        if node_chain_id is not None and configured_chain is not None and node_chain_id != configured_chain:
            raise RuntimeError(f"Configured CHAIN_ID {configured_chain} does not match provider chain id {node_chain_id}")

        self.chain_id = node_chain_id or configured_chain
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
        """Load an ABI from a filepath or a JSON string/artifact.

        The function returns the ABI list suitable for passing to web3.eth.contract.
        It will raise a ValueError if it cannot find a valid ABI list.
        """
        if os.path.exists(path):
            with open(path, 'r') as fh:
                parsed = json.load(fh)
        else:
            parsed = json.loads(path)

        # If it's a compiled artifact with an 'abi' key, return that
        if isinstance(parsed, dict):
            if 'abi' in parsed and isinstance(parsed['abi'], list):
                return parsed['abi']
            if 'data' in parsed and isinstance(parsed['data'], dict) and 'abi' in parsed['data'] and isinstance(parsed['data']['abi'], list):
                return parsed['data']['abi']
            raise ValueError('ABI JSON does not contain an "abi" list')

        if isinstance(parsed, list):
            return parsed

        raise ValueError('Invalid ABI content')

    def get_contract(self):
        if not self._contract:
            if not (self.contract_address and self.abi):
                raise RuntimeError("Contract address or ABI not configured")
            self._contract = self.w3.eth.contract(address=self.contract_address, abi=self.abi)
        return self._contract

    def call(self, method_name: str, *args):
        contract = self.get_contract()
        method = getattr(contract.functions, method_name)
        return method(*args).call()

    def _prepare_fees(self, tx: Dict) -> None:
        """Populate EIP-1559 fee fields when supported, otherwise set legacy gasPrice.

        This mutates the tx dict in-place.
        """
        # Query pending block for baseFeePerGas (EIP-1559)
        try:
            pending = self.w3.eth.get_block('pending')
        except Exception:
            pending = None

        base_fee = None
        if pending is not None:
            # AttributeDict supports .get and also item access; try both safely
            try:
                base_fee = pending.get('baseFeePerGas', None)  # type: ignore[attr-defined]
            except Exception:
                try:
                    base_fee = pending['baseFeePerGas']  # type: ignore[index]
                except Exception:
                    base_fee = getattr(pending, 'baseFeePerGas', None)

        if base_fee is not None:
            # Use EIP-1559 fields
            tx.pop('gasPrice', None)
            # Try to get node suggested max priority fee
            priority = None
            try:
                maybe = getattr(self.w3.eth, 'max_priority_fee', None)
                if callable(maybe):
                    priority = maybe()
                else:
                    priority = maybe
            except Exception:
                priority = None

            if not priority:
                priority = int(self.w3.to_wei(2, 'gwei'))

            # Set sensible default for max fee (avoid float ops)
            max_fee = int(int(base_fee) * 2 + int(priority))

            tx.setdefault('maxPriorityFeePerGas', int(priority))
            tx.setdefault('maxFeePerGas', int(max_fee))
            # mark as type 2 (EIP-1559) so signing libraries are explicit
            tx.setdefault('type', 2)
        else:
            # Fallback to legacy gasPrice
            if 'gasPrice' not in tx:
                tx['gasPrice'] = self.w3.eth.gas_price

    def build_tx(self, function_name: str, args: Sequence[Any], tx_from: str, gas: Optional[int] = None, gas_price: Optional[int] = None, value: int = 0) -> Dict:
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

        # Estimate gas if not present - let exceptions bubble up
        if 'gas' not in tx:
            estimated = self.w3.eth.estimate_gas(tx)
            tx['gas'] = int(estimated * 1.2)

        return tx

    def sign_and_send_raw_tx(self, tx: Dict) -> str:
        if not self.private_key:
            raise RuntimeError('No private key configured for signing transactions')

        # Ensure chainId is present
        if 'chainId' not in tx and self.chain_id is not None:
            tx['chainId'] = self.chain_id

        # Prepare gas pricing (may raise) - let errors propagate
        self._prepare_fees(tx)

        # Sign and send
        signed = Account.sign_transaction(tx, self.private_key)
        # eth-account returns a SignedTransaction object whose raw bytes attribute
        # may be `raw_transaction` (newer versions) or `rawTransaction` (older).
        raw = getattr(signed, 'raw_transaction', None) or getattr(signed, 'rawTransaction', None)
        if raw is None:
            raise RuntimeError('Signed transaction object does not contain raw bytes')
        tx_hash = self.w3.eth.send_raw_transaction(raw)
        return self.w3.to_hex(tx_hash)

    def send_transaction(self, function_name: str, args: Sequence[Any], tx_from: Optional[str] = None, wait_for_receipt: bool = False, timeout: int = 120) -> Dict:
        """Build, sign and send a tx calling contract.function_name(*args).

        Returns a dict with at least 'tx_hash'. If wait_for_receipt True, returns the receipt under 'receipt'.
        Exceptions are propagated to the caller.
        """
        if not tx_from:
            if not self.private_key:
                raise RuntimeError('tx_from must be provided when no private key is configured')
            acct = Account.from_key(self.private_key)
            tx_from = acct.address

        tx = self.build_tx(function_name, args, tx_from)

        tx_hash = self.sign_and_send_raw_tx(tx)

        result: Dict[str, Optional[Any]] = {'tx_hash': tx_hash}
        if wait_for_receipt:
            receipt = self.wait_for_receipt(tx_hash, timeout=timeout)
            result['receipt'] = dict(receipt) if receipt else None
        return result

    def wait_for_receipt(self, tx_hash: str, timeout: int = 120, poll_interval: float = 2.0):
        # Use web3.wait_for_transaction_receipt which raises on timeout - propagate that
        return self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)

    def compute_voter_hash(self, types: Sequence[str], values: Sequence[Any]) -> str:
        """Compute a solidity keccak hash for the provided types and values.

        Example: compute_voter_hash(['uint256','string'], [election_id, registration_number])
        returns hex string (0x...)
        """
        h = self.w3.solidity_keccak(list(types), list(values))
        return self.w3.to_hex(h)
