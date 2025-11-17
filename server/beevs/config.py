import os
from datetime import timedelta
from dotenv import load_dotenv


load_dotenv(override=True)


class Config:
    APP_ENV = os.getenv("APP_ENV", "production")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "86400")))  # 1 day
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", "2592000")))  # 30 days
    JWT_ALGORITHM = "HS256"
    WEB3_PROVIDER_URL = os.getenv("WEB3_PROVIDER_URL")
    CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
    CONTRACT_ABI_PATH = os.getenv("CONTRACT_ABI_PATH")
    RELAYER_PRIVATE_KEY = os.getenv("RELAYER_PRIVATE_KEY")
    CHAIN_ID = int(os.getenv("CHAIN_ID", "1"))
    TX_CONFIRMATIONS = int(os.getenv("TX_CONFIRMATIONS", "1"))