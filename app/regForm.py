from wtforms import Form, StringField,validators,PasswordField,BooleanField
from flask import render_template, flash, request, url_for, redirect

class RegistrationForm(Form):
    username = StringField('Username',[validators.Length(min=4, max=20)])
    email = StringField('Email Address',[validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.DataRequired(),
                                          validators.EqualTo('confirm',
                                                             message="Password must match.")])
    confirm = PasswordField('Repeat Password')

    accept_tos = BooleanField('I accept the <a href="/tos/"> Terms of Service </a> and '
                              'the <a href="/privacy/"> Privacy Notice </a> Last updated Aug 2017',
                              [validators.DataRequired()])

