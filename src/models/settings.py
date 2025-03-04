# third party model
from pydantic_settings import BaseSettings
from pydantic import SecretStr
from pymongo import MongoClient


# build in model
import os


# .env file path
root_path = os.path.abspath('src')
env_path = os.path.join(root_path, '.env')


class Settings(BaseSettings):
    """loading configuration from environment variables

    Args:
        BaseSettings: load enviroment variables
    """
    # Email
    SENDER_EMAIL: SecretStr
    SENDER_PASSWORD: SecretStr

    # JWT Secret Key
    ADMIN_SECRET_JWT: SecretStr
    USER_SECRET_JWT: SecretStr

    # JWT Access Token
    ADMIN_SECRET_ACCESS_TOKEN: SecretStr
    USER_SECRET_ACCESS_TOKEN: SecretStr

    # setting config
    class Config:
        env_file = env_path
        env_file_encoding = 'utf-8'
        extra = 'allow'


# Instance
settings = Settings()


class MongoConfig(BaseSettings):
    # Mongo Config
    HOST: str
    PORT: int
    DB: str
    USER: str
    PASSWORD: SecretStr

    class Config:
        env_file = env_path
        env_file_encoding = 'utf-8'
        extra = 'allow'


# Instance
mongo_config = MongoConfig()
client = MongoClient(mongo_config.HOST, mongo_config.PORT)
db = client[mongo_config.DB]
