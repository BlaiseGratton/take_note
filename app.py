from flask import Flask, render_template

from peewee import *

app = Flask(__name__)

database = SqliteDatabase('take_note_database')

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

@app.route('/<name>')
def index(name="Colby"):
    return render_template("index.html", name=name)

@app.route('/notes')
def notes(note1="CRUD is crud!", note2="I'm sad today", note3="Today I'm not!"):
    context = {'note1': note1, 'note2': note2, 'note3': note3}
    return render_template("notes.html", notes=context)

@app.route('/notes/<note>')
def note(note="Today I am sad"):
    return render_template("note.html", note=note)

# @app.route('/notes/<note>')

if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')
