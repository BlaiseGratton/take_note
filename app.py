#! usr/bin/env python

from datetime import datetime
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
    title = CharField()

    class Meta:
        order_by = ('-pub_date',)

def create_tables():
    database.connect()
    database.create_tables([User, Notes])

def auth_user(user):
    session['logged_in'] = True
    session['user'] = user
    session['username'] = user.username
    flash('You are logged in as %s' % (user.username))

def login_required(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return inner

def create_user():
    try:
        with database.transaction():
            user = User.create(
                username=request.form['username'],
                password=md5(request.form['password']).hexdigest(),
                email=request.form['email'],
                join_date=datetime.datetime.now()
            )
        auth_user(user)
        return redirect(url_for('homepage'))
    except IntegrityError:
        flash('That username is already taken')

user = get_object_or_404(User, username=username)
try:
    with database.transaction():
        Relationship.create(
                from_user=get_current_user(),
                to_user=user)
except IntegrityError:
    pass

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
