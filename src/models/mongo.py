# third party modules
from mongoengine import (
    connect, Document, ReferenceField, ListField,
    StringField, IntField, EmailField, DateTimeField
)

# local modules
from src.models.settings import mongo_config


DATABASE = mongo_config.DB
HOST = mongo_config.HOST
PORT = mongo_config.PORT

connect(DATABASE, host=HOST, port=PORT)


class UserDetails(Document):
    username = StringField(required=True)
    email = EmailField(required=True)
    days = IntField(required=True)
    issue_date = DateTimeField(required=True)
    due_warning = DateTimeField(required=True)
    due_date = DateTimeField(required=True)
    meta = {
        'collection': 'UserDetails'
    }


class Books(Document):
    # id = IntField(required=True, unique=True)
    title = StringField(required=True)
    author = StringField(required=True)
    available = IntField(required=True, min_value=0)
    user_details = ListField(ReferenceField(UserDetails, required=False))
    meta = {
        'collection': 'Books'
    }


class Department(Document):
    name = StringField(required=True, unique=True)
    books = ListField(ReferenceField(Books))
    meta = {
        'collection': 'Department'
    }
