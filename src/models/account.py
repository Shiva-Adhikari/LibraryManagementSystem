# third party module
from mongoengine import (
    # IntField,
    StringField, EmailField, ListField, ReferenceField, Document
)


class AccountDetails(Document):
    # id = IntField(required=True)
    username = StringField(required=True, unique=True)
    email = EmailField(required=False)
    password = StringField(required=True)
    meta = {
        'collection': 'AccountDetails'
    }


class Account(Document):
    account = StringField(required=True, unique=True)
    account_details = ListField(ReferenceField(AccountDetails))
    meta = {
        'collection': 'Account'
    }
