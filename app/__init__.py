# coding=utf-8
from flask import Flask, render_template, request, redirect, flash, url_for, session, g
from app import data
from regForm import RegistrationForm
from passlib.hash import sha256_crypt
from register_and_login import Register, Log_in
from functools import wraps
import gc

app = Flask(__name__)
# ему тут не место, он должен быть в файлу flaskapp.wsgi чтобы его никто не своровал
app.secret_key = 'your secret key. If you share your website, do NOT share it with this key'


# Декоратор для входа в систему, loguot чтобы можно было сделать
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to log in first')
            return redirect(url_for('login_page'))
    return wrap


@app.route('/')
def homepage():
    return render_template('main.html',
                           welcome=data.welcome)


@app.route('/logout/')
@login_required
def logout_page():
    session.clear()
    flash('you have been logged out!')
    gc.collect()
    return redirect(url_for('homepage'))


@app.route('/login/', methods=['GET', 'POST'])
def login_page():
    error = ''
    try:
        user = Log_in()
        if request.method == "POST":
            check_user = user.login_user(request.form['username'])
            if check_user == 'bad':
                error = 'Such a user does not exist'
                return render_template('login.html',
                                       error=error,
                                       title="Log in")
            if sha256_crypt.verify(request.form['password'], user.get_pwd(request.form['username'])):
                session['logged_in'] = True
                session['username'] = request.form['username']
                flash('You are logged in!!')
                return redirect(url_for('homepage'))
            else:
                error = 'Incorrect password. Try again.'
        gc.collect()
        return render_template('login.html',
                               title="Log in",
                               error=error)
    except Exception as e:
        return render_template('login.html',
                               error=error,
                               title='Log in')


@app.route('/register/', methods=['GET', 'POST'])
def register_page():
    try:
        form = RegistrationForm(request.form)
        add_usr = Register()
        if request.method == "POST":
            username = request.form['username']
            email = request.form['email']
            password = sha256_crypt.encrypt(str(request.form['password']))
            check = add_usr.new_user(username, email, password, '/')
            if check != 'ok':
                flash(check)
                return render_template('register.html',
                                       form=form,
                                       title='Sign up')
            else:
                flash('Thanks for registering!')
                gc.collect()
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('homepage'))

        return render_template('register.html',
                               form=form,
                               title='Sign up')
    except Exception as e:
        return str(e)


# Обработчики ошибок на сайте. 404 - если страница не найдена и 405 - если метода нет
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html",
                           title='Woops')


@app.errorhandler(405)
def method_not_perm():
    return render_template('405.html',
                           title="Woops")


if __name__ == "__main__":
    app.run()
