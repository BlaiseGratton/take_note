#! usr/bin/env python

from flask import (flash, Flask, g, request, 
                   redirect, render_template, url_for)
from flask.ext.bcrypt import check_password_hash
from flask.ext.login import (LoginManager, login_user,
                             logout_user, login_required)

import forms
import models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'iwnv847*345798^^#*(vs&348agxcvifj**w9'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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

@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None

@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()

@app.after_request
def after_request(response):
    """Close the database connection after each request."""
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
