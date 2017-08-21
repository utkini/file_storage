from flask import render_template, flash, request, url_for, redirect,session
from app import app
from registration import RegistrationForm
from dbconnection import connection
from passlib.hash import sha256_crypt

form = RegistrationForm(request.form)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    error = ''
    try:
        if request.method == "POST":
            attempted_username = request.form['username']
            attempted_password = request.form['password']

            flash(attempted_username)
            flash(attempted_password)

            if attempted_username == 'admin' and attempted_password == 'password':
                return redirect(url_for('index'))
            else:
                error = 'Invalid credential. Try again.'
        return render_template('login.html', error=error)
    except Exception as e:
        flash(e)
        return render_template('login.html', error=error)


@app.route('/')
def homepage():
    return render_template('main.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


@app.route('/register/', methods=['GET', 'POST'])
def register_page():
    try:
        if request.method == 'POST' and form.validate():
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            db , coll = connection()
    except Exception as e:
        return (str(e))
