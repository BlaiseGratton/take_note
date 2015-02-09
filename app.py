#! usr/bin/env python
from flask import Flask, g, request, redirect, render_template
from peewee import *

app = Flask(__name__)

DATABASE = 'take_note.db'

database = SqliteDatabase(DATABASE, threadlocals=True)

class BaseModel(Model):
    class Meta:
        database = database

class User(BaseModel):
    username = CharField(unique=True)
    password = CharField()
    email = CharField()
    join_date = DateTimeField()

class Notes(BaseModel):
    user = ForeignKeyField(User)
    content = TextField()
    pub_date = DateTimeField()

    class Meta:
        order_by = ('-pub_date',)

def create_tables():
    database.connect()
    database.create_tables([User, Notes])

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
def after_request():
    g.db.close()
    return response

@app.route('/<name>')
def index(name="user"):
    return render_template("index.html", name=name)

@app.route('/notes')
def notes(user=User()):
    context = get_user_notes(user)
    return render_template("notes.html", notes=context)

@app.route('/notes/<note>')
def note(note="Today I am sad"):
    return render_template("note.html", note=note)

if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')
