# coding=utf-8
from flask import Flask, render_template, request, redirect, flash, url_for
from app import data

app = Flask(__name__)
# ему тут не место, он должен быть в файлу flaskapp.wsgi чтобы его никто не своровал
app.secret_key = 'your secret key. If you share your website, do NOT share it with this key'


@app.route('/home/')
@app.route('/')
def homepage():
    return render_template('main.html',
                           welcome=data.welcome)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


@app.route('/login/', methods=['GET', 'POST'])
def login():
    error = ''
    try:
        if request.method == "POST":
            attempted_username = request.form['email']
            attempted_password = request.form['password']

            flash(attempted_username)
            flash(attempted_password)

            if attempted_username == 'admin' and attempted_password == 'password':
                return redirect(url_for('main.html'))
            else:
                error = 'Invalid credential. Try again.'
        return render_template('login.html',
                               title="Log In",
                               error=error)
    except Exception as e:
        return str(e)


if __name__ == "__main__":
    app.run()
