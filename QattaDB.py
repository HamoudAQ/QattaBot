from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
import datetime
import os.path

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
    desc = TextField()
    date = DateTimeField(default=datetime.datetime.now)




db_file=os.path.isfile('QattaDB.db')
if not db_file: #if you changed the DB model then don't forget to delete the QattaDB.db file
    db.create_tables([User, Chat, Count, Entry])


