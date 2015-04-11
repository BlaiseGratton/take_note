#! usr/bin/env python

from datetime import datetime
from flask import Flask, g, request, redirect, render_template
from flask.ext.bcrypt import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from peewee import *

app = Flask(__name__)

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

def create_tables():
    DATABASE.connect()
    DATABASE.create_tables([User, Note, Category])

def auth_user(user):
    session['logged_in'] = True
    session['user'] = user
    session['username'] = user.username
    flash('You are logged in as %s' % (user.username))

def get_user_notes(self):
    return (User
            .select()
            .join(Notes, on=Notes.user)
            .where(Notes.user == self.username))

@app.before_request
def before_request():
    g.db = database
    g.db.connect()

@app.after_request
def after_request(response):
    g.db.close()
    return response

@app.route('/<name>')
def index(name="user"):
    return render_template("index.html", name=name)

@app.route('/<name>/newnote')
def newnote(name="user"):
    return render_template("newnote.html", name=name)

@app.route('/<name>/notes')
def notes(user=User()):
    context = get_user_notes(user)
    return render_template("notes.html", notes=context)

@app.route('/<name>/<note>')
def note(name="user", note="Today I am sad"):
    return render_template("note.html", note=note)

if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')
