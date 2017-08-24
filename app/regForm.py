from wtforms import Form, StringField,validators,PasswordField
from flask import render_template, flash, request, url_for, redirect

class RegistrationForm(Form):
    username = StringField('Username',[validators.Length(min=4, max=20)])
    email = StringField('Email Address',[validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.DataRequired(),
                                          validators.EqualTo('confirm',
                                                             message="Password must match.")])
    confirm = PasswordField('Repeat Password')


