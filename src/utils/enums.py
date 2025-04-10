from enum import Enum

from src.models.settings import settings, mongo_config, http_server


class Env(Enum):
    SENDER_EMAIL = settings.SENDER_EMAIL.get_secret_value()
    SENDER_PASSWORD = settings.SENDER_PASSWORD.get_secret_value()
    ADMIN_SECRET_JWT = settings.ADMIN_SECRET_JWT.get_secret_value()
    USER_SECRET_JWT = settings.USER_SECRET_JWT.get_secret_value()
    JWT_ALGORITHM = settings.JWT_ALGORITHM.get_secret_value()
    ADMIN_SECRET_ACCESS_TOKEN = settings.ADMIN_SECRET_ACCESS_TOKEN.get_secret_value()
    USER_SECRET_ACCESS_TOKEN = settings.USER_SECRET_ACCESS_TOKEN.get_secret_value()

    HOST = mongo_config.HOST
    PORT = mongo_config.PORT
    DB = mongo_config.DB
    USER = mongo_config.USER
    PASSWORD = mongo_config.PASSWORD.get_secret_value()

    HTTPSERVER_PORT = http_server.HTTPSERVER_PORT
