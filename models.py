import datetime

from flask.ext.bcrypt import generate_password_hash
from flask.ext.login import UserMixin
from peewee import *

DATABASE = SqliteDatabase('take_note.db', threadlocals=True)

class BaseModel(Model):
    class Meta:
        database = DATABASE

class User(UserMixin, BaseModel):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    join_date = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        order_by = ('-join_date',)

    @classmethod
    def create_user(cls, username, email, password, admin=False):
        try:
            cls.create(
                username=username,
                email=email, 
                password=generate_password_hash(password),
                is_admin=admin)
        except IntegrityError:
            raise ValueError("User already exists")

class Category(BaseModel):
    name = CharField(unique=True, max_length=100)

class Note(BaseModel):
    user = ForeignKeyField(User)
    content = TextField()
    pub_date = DateTimeField(default=datetime.datetime.now)
    title = CharField(max_length=100)
    category = ForeignKeyField(Category)

    class Meta:
        order_by = ('-pub_date',)

class Category(BaseModel):
    name = CharField(unique=True, max_length=100)

def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Note, Category], safe=True)
    DATABASE.close()
