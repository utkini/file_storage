from flask import render_template, flash, Flask, request, url_for, redirect
from app import app



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
        return render_template('login.html', error = error)
    except Exception as e:
        flash(e)
        return render_template('login.html', error = error)


@app.route('/')
@app.route('/index')
def index():
    user = { 'nickname': 'Igor'}
    posts = [
        {
            'author': {'nickname': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'nickname': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html',
                           title = 'home',
                           user = user,
                           posts = posts)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")
