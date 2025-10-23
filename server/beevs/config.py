import os
from dotenv import load_dotenv


load_dotenv(override=True)


class Config:
    APP_ENV = os.getenv("APP_ENV", "production")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False