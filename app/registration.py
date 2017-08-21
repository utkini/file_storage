from wtforms import Form, TextField,validators,PasswordField,BooleanField
from flask import render_template, flash, request, url_for, redirect

class RegistrationForm(Form):
    username = TextField('Username',[validators.Length(min=4, max=20)])
    email = TextField('Email Address',[validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.Required(),
                                          validators.EqualTo('confirm',
                                                             message="Password must math.")])
    confirm = PasswordField('Repeat Password')

    accept_tos = BooleanField('I accept the <a href="/tos/"> Terms of Service </a> and '
                              'the <a href="/privacy/"> Privacy Notice </a> Last updated Aug 2017',
                              [validators.Required()])

