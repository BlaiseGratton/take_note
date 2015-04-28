#! usr/bin/env python

from flask import (abort, flash, Flask, g,
                   redirect, render_template, url_for)
from flask.ext.bcrypt import check_password_hash
from flask.ext.login import (current_user, LoginManager, login_user,
                             logout_user, login_required)

import datetime
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
    g.user = current_user

@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response

@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("User successfully registered", "success")
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password is not correct", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("User successfully logged in", "success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password is not correct", "error")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("User successfully logged out", "success")
    return redirect(url_for('index'))

@app.route('/new_note', methods=('GET', 'POST'))
@login_required
def new_note():
    form = forms.NoteForm()
    if form.validate_on_submit():
        models.Note.create(
            user = g.user._get_current_object(),
            content = form.content.data.strip(),
            title = form.title.data,
            category = form.category.data
        )
        flash("New note created on " + "{:%B %d, %Y}".format(datetime.datetime.now()), "success")
        return redirect(url_for('notes'))
    return render_template('newnote.html', form=form)

@app.route('/new_category', methods=('POST'))
@login_required
def new_category():
    form = forms.CategoryForm()
    if form.validate_on_submit():
        models.Category.create(name = form.name.data.strip())
        flash("Successfully added category", "success")
        return
    flash("There was an error adding the category", "error")
    return

@app.route('/notes')
@login_required
def notes():
    user = g.user._get_current_object()
    notes = models.Note.select().where(models.Note.user == user.id)
    return render_template('notes.html', notes=notes)

@app.route('/notes/<int:note_id>')
@login_required
def note(note_id):
    try:
        note = models.Note.select().where(
                models.Note.id == note_id).get()
    except models.DoesNotExist:
        abort(404)
    if note.user.id != g.user._get_current_object().id:
        flash("You do not have authorization for that note", "error")
        return redirect(url_for('notes'))
    return render_template('note.html', note=note)

@app.route('/notes/delete/<int:note_id>')
@login_required
def delete_note(note_id):
    try:
       note = models.Note.get(id=note_id, user=g.user._get_current_object().id).delete_instance()
    except models.DoesNotExist:
        flash("That note does not exist", "error")
        return redirect(url_for('notes'))
    flash("Note successfully deleted")
    return redirect(url_for('notes'))

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username='BlaisezFaire',
            email='blaisegratton@gmail.com',
            password='asdfasdf',
            admin=True
        )
    except ValueError:
        pass
    app.run(debug=DEBUG, host=HOST, port=PORT)
