# third party modules
from mongoengine import (
    connect,
    IntField,
    StringField,
    ListField,
    EmbeddedDocument,
    DynamicDocument
)

# local modules
from src.models.settings import mongo_config


DATABASE = mongo_config.DB
HOST = mongo_config.HOST
PORT = mongo_config.PORT

connect(DATABASE, host=HOST, port=PORT)


class BookCategories(EmbeddedDocument):
    Id = IntField()
    Title = StringField()
    Author = StringField()
    Available = IntField()


class Books(DynamicDocument):
    books = ListField()
    meta = {
        'collection': 'Books'
    }
