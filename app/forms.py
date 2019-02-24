from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField,DateTimeField,SelectField
from wtforms.validators import DataRequired,Email

class LoginForm(FlaskForm):
    mail = StringField('mail', validators=[DataRequired(),Email()])
    password = StringField('password',validators=[DataRequired()])
    remember = BooleanField('remember')


class registerForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    qq = StringField('qq')
    mail = StringField('mail', validators=[DataRequired(),Email()])
    password = StringField('password', validators=[DataRequired()])
    passwordagain = StringField('passwordagain', validators=[DataRequired()])


class resForm(FlaskForm):
    passwordag = StringField('passwordag', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])


class editForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    dec = StringField('dec')
    start = DateTimeField('start', validators=[DataRequired()],format='%Y-%m-%d %H:%M')
    end = DateTimeField('end', validators=[DataRequired()],format='%Y-%m-%d %H:%M')

class profileForm(FlaskForm):
    old = StringField('old')
    new = StringField('new')
    newag = StringField('newag')
    qq = StringField('qq')
    open = BooleanField('open')