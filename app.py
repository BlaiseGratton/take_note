#! usr/bin/env python

from datetime import datetime
from flask import Flask, g, request, redirect, render_template
from flask.ext.bcrypt import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from peewee import *

import models

app = Flask(__name__)

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
