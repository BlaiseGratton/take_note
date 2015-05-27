#! usr/bin/env python

from flask import (abort, flash, Flask, g, jsonify,
                   redirect, render_template, request, url_for)
from flask.ext.bcrypt import check_password_hash
from flask.ext.login import (current_user, LoginManager, login_user,
                             logout_user, login_required)

import datetime
import forms
import math
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
                return redirect(url_for('notes'))
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
    user = g.user._get_current_object()
    categories = models.Category.select().where(models.Category.user == user.id)
    if form.validate_on_submit():
        models.Note.create(
            user = user,
            content = form.content.data.strip(),
            title = form.title.data,
            category = form.category.data
        )
        flash("New note created on " + "{:%B %d, %Y}".format(datetime.datetime.now()), "success")
        return redirect(url_for('notes'))
    return render_template('newnote.html', form=form, categories=categories)

@app.route('/new_category')
@login_required
def new_category():
    name = request.args.get('name')
    addedCategory = models.Category.create(
        name=name,
        user = g.user._get_current_object()
    )
    return jsonify(name=addedCategory.name, id=addedCategory.id)

@app.route('/notes', defaults={'page':1})
@app.route('/notes/<int:page>')
@login_required
def notes(page):
    user = g.user._get_current_object()
    entries = user.entries*1.0
    pages = math.ceil(models.Note.select().where(models.Note.user == user.id).count()/entries)
    page_range = list(range(1,int(pages+1)))
    notes = models.Note.select().where(models.Note.user == user.id).paginate(page, entries)
    try:
        notes[0]
        if page not in page_range:
            return redirect(url_for('notes'))
    except IndexError:
        pass
    return render_template('notes.html', notes=notes, pages=page_range, current_page=page)

@app.route('/note/<int:note_id>')
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

@app.route('/note/<int:note_id>/edit', methods=('GET', 'POST'))
@login_required
def edit_note(note_id):
    try:
        note = models.Note.select().where(models.Note.id == note_id).get()
    except models.DoesNotExist:
        abort(404)
    if note.user.id != g.user._get_current_object().id:
        flash("You do not have authorization for that note", "error")
        return redirect(url_for('notes'))
    form = forms.NoteForm(request.form, obj=note)
    if form.validate_on_submit():
        form.populate_obj(note)
        note.save()
        return redirect(url_for('note', note_id=note.id))
    categories = models.Category.select()
    return render_template('edit_note.html', form=form, categories=categories)

@app.route('/note/delete/<int:note_id>')
@login_required
def delete_note(note_id):
    try:
       note = models.Note.get(id=note_id, user=g.user._get_current_object().id).delete_instance()
    except models.DoesNotExist:
        abort(404)
    flash("Note successfully deleted", "success")
    return redirect(url_for('notes'))

@app.route('/search/', methods=('GET', 'POST'))
@login_required
def search():
    form=forms.SearchForm()
    if form.validate_on_submit():
        user = g.user._get_current_object()
        search_term = form.search_term.data
        results=[]
        if not form.search_date.data and search_term:
            results = models.Note.select().where(
                        models.Note.user == user.id
                    ).select().where(
                        (models.Note.content.contains(search_term)) | 
                        (models.Note.title.contains(search_term))
                    )
        if form.search_date.data:
            results = models.Note.select().where(
                        models.Note.user == user.id
                    )
            if form.date_operator.data == 'before':
                results = results.select().where(models.Note.pub_date < form.search_date.data)
            if form.date_operator.data == 'on':
                results = results.select().where(
                            (models.Note.pub_date.year == form.search_date.data.year) and
                            (models.Note.pub_date.month == form.search_date.data.month) and
                            (models.Note.pub_date.day == form.search_date.data.day)
                        )
            if form.date_operator.data == 'after':
                results = results.select().where(models.Note.pub_date > form.search_date.data)
            results = results.select().where(
                        (models.Note.content.contains(search_term)) |
                        (models.Note.title.contains(search_term))
                    )
        try:
            results[0]
        except IndexError:
            flash("No matches found", "error")
            return render_template('search.html', form=form)
        return render_template('search.html', form=form, results=results)
    return render_template('search.html', form=form)

@app.route('/settings', methods=('GET', 'POST'))
def settings():
    form = forms.SettingsForm()
    if form.validate_on_submit():
        user = g.user._get_current_object()
        paginate_setting = form.paginate_range.data
        return render_template('settings.html', form=form, paginate_range=paginate_setting)
    return render_template('settings.html', form=form)

@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

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
