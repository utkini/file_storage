# coding=utf-8
from flask import Flask, render_template, request, redirect, flash, url_for, session, g,send_from_directory
from regForm import RegistrationForm
from passlib.hash import sha256_crypt
from register_and_login import Register, LogIn
from functools import wraps
import gc
import os

UPLOAD_FOLDER = '/home/ihgorek/Documents/file_storage/app/5e'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
# ему тут не место, он должен быть в файлу flaskapp.wsgi чтобы его никто не своровал
app.secret_key = 'your secret key. If you share your website, do NOT share it with this key'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_filename(filename):
    return filename.replace('/','_')




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


@app.route('/', methods=['GET', 'POST'])
def homepage():
    try:
        return render_template('main.html')
    except Exception as e:
        return str(e)


@app.route('/login/', methods=['GET', 'POST'])
def login_page():
    error = ''
    try:
        user = LogIn()
        if request.method == "POST":
            check_user = user.login_user(request.form['username'])
            if check_user == 'bad':
                error = 'Such a user does not exist'
                return render_template('login.html',
                                       error_u=error)
            if sha256_crypt.verify(request.form['password'], user.get_pwd(request.form['username'])):
                session['logged_in'] = True
                session['username'] = request.form['username']
                flash('You are logged in!!')
                return render_template('main.html')
            else:
                error = 'Incorrect password. Try again.'
        gc.collect()
        return render_template('login.html',
                               error_p=error)
    except Exception as e:
        return render_template('login.html',
                               error=e,
                               title='Log in')


@app.route('/register/', methods=['GET', 'POST'])
def register_page():
    try:
        form = RegistrationForm(request.form)
        new_user = Register()
        if request.method == "POST" and form.validate():
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt(str(form.password.data))
            check = new_user.add_user(username, email, password, '/')
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


@app.route('/logout/')
@login_required
def logout_page():
    session.clear()
    flash('you have been logged out!')
    gc.collect()
    return redirect(url_for('homepage'))


@app.route('/home/<user>/<diri>')
def home_user(user, diri):
    return render_template('main.html',
                           d=user,
                           dirs=diri)


@app.route('/home/')
def home():
    c = '/home/ihgorek/Documents/file_storage/app/5e'
    ans = os.walk(c)
    d, dirs, files = next(ans)
    d = d.split('/')
    return render_template('home.html',
                           d=d,
                           dirs=dirs,
                           files=files)


@app.route('/settings/',methods=['GET','POST'])
def settings():
    if request.args.values():
        return 'hyh'
    else:
        return render_template('settings.html')


@app.route('/uploads', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''



@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


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
