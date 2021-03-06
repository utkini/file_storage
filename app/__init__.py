# coding=utf-8
import gc
import os
from functools import wraps

from flask import Flask, render_template, request, redirect, flash, url_for, session, send_file
from passlib.hash import sha256_crypt
from werkzeug.utils import secure_filename

from api.register_and_login import Register, LogIn
from api.usersdata import UsersData
from regForm import RegistrationForm

UPLOAD_FOLDER = '/home/user1/my_flask_app/users'
ALLOWED_EXTENSIONS = {'txt', 'doc', 'docx', 'docm', 'dotm', 'dotx', 'pdf',  # TEXT
                      'xls', 'xlsx', 'xlsm', 'xltx', 'xlt', 'xltm', 'pptx',
                      'ppt', 'ppsx', 'pps', 'potx', 'pot', 'ppa', 'ppam',
                      'jpg', 'jpeg', 'tif', 'tiff', 'png', 'gif', 'bmp',  # PICTURE
                      'wav', 'mp3', 'wma', 'ogg', 'aac', 'flac'  # SONG
                      'avi','mkv','mp4','mpeg'} # VIDEO
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
# ему тут не место, он должен быть в файлу flaskapp.wsgi чтобы его никто не своровал
app.secret_key = 'your secret key. If you share your website, do NOT share it with this key'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
                error = "Such a user doesn't exist"
                return render_template('login.html',
                                       error_u=error)
            if sha256_crypt.verify(request.form['password'], user.get_pwd(request.form['username'])):
                session['logged_in'] = True
                session['username'] = request.form['username']
                session['user_id'] = user.get_user_id(session['username'])
                flash('You are logged in!!')
                return redirect(url_for('home_user', pathway=session['username']))
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
                session['user_id'] = new_user.get_id_user(username)
                users_file = UsersData()
                users_file.create_dir_for_user(session['username'], session['user_id'])
                return redirect(url_for('home_user', pathway=session['username']))

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


@app.route('/home/<path:pathway>', methods=['GET', 'POST'])
@login_required
def home_user(pathway):
    try:
        username = pathway.split('/')[0]
        user_file = UsersData()
        user = LogIn()
        folders = user_file.get_folder(username, session['user_id'], pathway)
        files = user_file.find_files_in_dirs(username, session['user_id'], pathway)
        dirs = user_file.get_dir(username, session['user_id'], pathway)
        if dirs == 'There is no such directory':
            return redirect(page_not_found)
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' in request.files:
                file = request.files['file']
                if file.filename == '':
                    flash('No selected file')
                    return redirect(request.url)
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    path_file = user_file.add_file(session['username'], session['user_id'], filename, pathway)
                    if type(path_file) == dict:
                        file.save(os.path.join(path_file['file_dir'], path_file['filename']))
                        return redirect(url_for('home_user',
                                                pathway=pathway))
                else:
                    flash('The extension of these files are not supported by this system.')
                    return redirect(url_for('home_user', pathway=pathway))
                    # файл есть
            # Форма для изменения имени директории в которой сейчас находится пользователь
            elif 'new_name_dir' in request.form:
                sep_path = pathway.split('/')
                change_dir = sep_path[-1]
                if len(request.form['new_name_dir']) < 15:
                    error = user_file.change_dir_name(session['username'], session['user_id'],
                                                      pathway, request.form['new_name_dir'])
                else:
                    error = 'This directory name is incorrect'
                if error is None:
                    tmp = pathway.split('/')
                    tmp[-1] = request.form['new_name_dir']
                    pathway = '/'.join(tmp)
                    dirs = user_file.get_dir(username, session['user_id'], pathway)
                    if dirs == 'There is no such directory':
                        return redirect(page_not_found)
                    folders = user_file.get_folder(session['username'], session['user_id'], pathway)
                    files = user_file.find_files_in_dirs(session['username'], session['user_id'], pathway)
                return render_template('home.html',
                                       pathway=dirs,
                                       folders=folders,
                                       files=files,
                                       error_dir=error)
            # Форма для создания папки в той директории, в которой находится пользователь.
            elif 'create_new_folder' in request.form:

                if request.form['create_new_folder'] and len(request.form['create_new_folder']) < 15:
                    way = pathway + '/' + request.form['create_new_folder']
                    error = user_file.create_folder(username, session['user_id'], way)
                else:
                    error = 'This field must be filled'
                dirs = user_file.get_dir(username, session['user_id'], pathway)
                if dirs == 'There is no such directory':
                    return redirect(page_not_found)
                folders = user_file.get_folder(session['username'], session['user_id'], pathway)
                files = user_file.find_files_in_dirs(session['username'], session['user_id'], pathway)
                return render_template('home.html',
                                       pathway=dirs,
                                       folders=folders,
                                       files=files,
                                       error_create_folder=error)

            # Форма удаления директории и всех в ней папой и файлов.
            elif 'del_dir_password' and 'del_dir' in request.form:
                if sha256_crypt.verify(request.form['del_dir_password'], user.get_pwd(session['username'])):
                    if request.form['del_dir']:
                        way = '/' + pathway + '/' + request.form['del_dir']
                        error = user_file.delete_dir(username, session['user_id'], way)
                    else:
                        error = 'This field must be filled'
                    dirs = user_file.get_dir(username, session['user_id'], pathway)
                    if dirs == 'There is no such directory':
                        return redirect(page_not_found)
                    folders = user_file.get_folder(session['username'], session['user_id'], pathway)
                    files = user_file.find_files_in_dirs(session['username'], session['user_id'], pathway)
                    return render_template('home.html',
                                           pathway=dirs,
                                           folders=folders,
                                           files=files,
                                           error_del_dir=error)
                else:
                    error = 'Incorrect password. Try again.'
                    return render_template('home.html',
                                           pathway=dirs,
                                           folders=folders,
                                           files=files,
                                           error_del_dir_p=error)
            # Форма для удаления файла
            elif 'del_file' and 'del_file_password' in request.form:
                if sha256_crypt.verify(request.form['del_file_password'], user.get_pwd(session['username'])):
                    error = user_file.del_file(username, session['user_id'], request.form['del_file'], pathway)
                    dirs = user_file.get_dir(username, session['user_id'], pathway)
                    if dirs == 'There is no such directory':
                        return redirect(page_not_found)
                    folders = user_file.get_folder(session['username'], session['user_id'], pathway)
                    files = user_file.find_files_in_dirs(session['username'], session['user_id'], pathway)
                    return render_template('home.html',
                                           pathway=dirs,
                                           folders=folders,
                                           files=files,
                                           error_del_file=error)
                else:
                    error = 'Incorrect password. Try again.'
                    return render_template('home.html',
                                           pathway=dirs,
                                           folders=folders,
                                           files=files,
                                           error_del_file_p=error)
            # Форма для переименования файла
            elif 'rename_file_new' and 'rename_file_old' in request.form:
                new_filename = secure_filename(request.form['rename_file_new'])
                error = user_file.rename_file(username, session['user_id'], pathway,
                                              request.form['rename_file_old'], new_filename)
                dirs = user_file.get_dir(username, session['user_id'], pathway)
                if dirs == 'There is no such directory':
                    return redirect(page_not_found)
                folders = user_file.get_folder(session['username'], session['user_id'], pathway)
                files = user_file.find_files_in_dirs(session['username'], session['user_id'], pathway)
                return render_template('home.html',
                                       pathway=dirs,
                                       folders=folders,
                                       files=files,
                                       error_rename_file=error)

        else:
            return render_template('home.html',
                                   pathway=dirs,
                                   folders=folders,
                                   files=files)
    except Exception as e:
        print str(e)


@app.route('/download/<path:filepath>')
@login_required
def send_files(filepath):
    filepath = UPLOAD_FOLDER + '/' + filepath
    print filepath
    return send_file(filepath, conditional=True)


@app.route('/settings/', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        user = LogIn()
        if 'email' and 'email_password' in request.form:
            if sha256_crypt.verify(request.form['email_password'], user.get_pwd(session['username'])):
                error = user.change_email(session['username'],session['user_id'],request.form['email'])
                if error is None:
                    flash('Email is changed')
                    return render_template('settings.html')
                else:
                    return render_template('settings.html',
                                           error_email=error)
            else:
                error = 'Incorrect password. Try again.'
                return render_template('settings.html',
                                       error_email_pwd=error)
        if 'old_password' and 'new_password' in request.form:
            password = sha256_crypt.encrypt(str(request.form['new_password']))
            if sha256_crypt.verify(request.form['old_password'], user.get_pwd(session['username'])):
                error = user.change_password(session['username'],session['user_id'],password)
                if error is None:
                    flash('Password has changed')
                    return render_template('settings.html')
                else:
                    return render_template('settings.html',
                                       error_new_p=error)
            else:
                error = 'Incorrect password. Try again.'
                return render_template('settings.html',
                                       error_old_p=error)

    else:
        return render_template('settings.html')


@app.route('/delete/')
@login_required
def delete_page():
    user = LogIn()
    user_files = UsersData()
    error_login = user.del_user(session['username'],session['user_id'])
    error_files = user_files.delete_user(session['username'],session['user_id'])
    if error_login is None and error_files is None:
        session.clear()
        flash('Your user has been deleted')
        gc.collect()
    else:
        flash("Something's wrong")
    return redirect(url_for('homepage'))


@app.route('/legal/terms/')
def terms():
    return render_template('terms.html')


@app.route('/legal/privacy/')
def privacy():
    return render_template('privacy.html')


@app.route('/support/')
def support():
    return render_template('support.html')


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
