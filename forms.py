from flask_wtf import Form
from wtforms import IntegerField, StringField, PasswordField, SelectField, TextAreaField
from wtforms.fields.html5 import DateField
from wtforms.validators import (DataRequired, Email, EqualTo,
                                Length, Optional, Regexp, ValidationError)

from models import User

def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with that name already exists.')

def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('User with that email already exists.')

class RegisterForm(Form):
    username = StringField(
        'Username', 
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message=("Username should be one word, letters, "
                    "numbers, and underscores only.")
            ),
            name_exists
        ])
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            email_exists
        ])
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=2),
            EqualTo('password2', message='Passwords must match')
        ])
    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired()]
    )

class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class NoteForm(Form):
   title = StringField('Title', validators=[DataRequired(message="Your note needs a title")])
   category = IntegerField('CategoryId', validators=[DataRequired(message="Please select a category")])
   content = TextAreaField("Your note...", validators=[DataRequired(message="A note about nothing?")])

class CategoryForm(Form):
    name = StringField('Name', validators=[DataRequired()])

class SearchForm(Form):
    search_term = StringField('Search')
    date_operator = SelectField(u'Operator', choices=[('before', 'Earlier than'), ('on', 'On'), ('after', 'Later than')])
    search_date = DateField('DatePicker', format='%Y-%m-%d', validators=[Optional()])

class SettingsForm(Form):
    paginate_range = SelectField(u'Pagination Range', coerce=int)
