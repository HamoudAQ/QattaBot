from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
import datetime

db = SqliteExtDatabase('QattaDB.db')

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    user = BigIntegerField(unique=True)
    name = CharField()

class Chat(BaseModel):
    chat = BigIntegerField(unique=True)

class Count(BaseModel):
    user = ForeignKeyField(User)
    chat = ForeignKeyField(Chat)
    count = DoubleField()

class Entry(BaseModel):
    user = ForeignKeyField(User)
    chat = ForeignKeyField(Chat)
    entry = DoubleField()
    desc = CharField()
    date = DateTimeField(default=datetime.datetime.now)

#db.create_tables([User, Chat, Count, Entry])
