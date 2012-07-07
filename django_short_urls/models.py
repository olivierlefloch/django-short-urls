from mongoengine import *

class User(Document):
    login = StringField(required=True, unique=True)
    api_key = StringField(required=True)
    email = StringField(required=True)

class Link(Document):
    short_path = StringField(required=True, unique=True)
    long_url = StringField(required=True)
