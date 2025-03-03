# third party model
from pydantic_settings import BaseSettings
from pydantic import SecretStr

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
    SENDER_EMAIL: SecretStr
    SENDER_PASSWORD: SecretStr

    # jwt secret key
    ADMIN_SECRET_JWT: SecretStr
    USER_SECRET_JWT: SecretStr

    # jwt secret access key
    ADMIN_SECRET_ACCESS_TOKEN: SecretStr
    USER_SECRET_ACCESS_TOKEN: SecretStr

    # setting config
    class Config:
        env_file = env_path
        env_file_encoding = 'utf-8'
        extra = 'allow'


# instance
settings = Settings()

# example to call values
# a = settings.SENDER_EMAIL.get_secret_value()
