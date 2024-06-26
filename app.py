from flask import Flask, render_template, request, redirect, flash, send_file
import os
from msg_worker import MSG_worker
import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'msg'}

all_users = MSG_worker.parse_users('users.txt')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_mails(input, users, output):
    msg = MSG_worker(filename=input,users=users)
    msg.extract_file(output)
    return output
def ch_users(usr,flag):
    usrs = MSG_worker(users=all_users,usr=usr, ch_usr=flag)
    usrs.set_users_file()

@app.route('/')
def index():
    return render_template('index.html', users=all_users)

def clear_uploads(folder):
    for filename in os.listdir(folder):
        os.remove(os.path.join(folder,filename))

@app.route('/send', methods=["GET", "POST"])
def send_data():

    if 'parse' in list(request.form.keys()):
        clear_uploads(app.config['UPLOAD_FOLDER'])
        if 'upload_file' not in request.files:
            flash('No file part')
            return redirect(request.url_root)
        files = list(request.files.values())
        if len(files[0].filename) == 0:
            flash('No selected file')
            return redirect(request.url_root)
        if not app.config['UPLOAD_FOLDER'] in os.listdir():
            os.mkdir(app.config['UPLOAD_FOLDER'])
        upload_file_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                        datetime.date.today().strftime('%d.%m.%Y') + '.msg')
        for file in files:
            itsok=allowed_file(file.filename)
            if itsok == False:
                flash('Wrong format')
                return redirect(request.url_root)

            file.save(upload_file_path)

        download_file_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                        datetime.date.today().strftime('%d.%m.%Y') + ' parsed' + '.txt')
        #Очень странно парсятся значения из формы с окончаниями /r/n
        users = [ x.replace('\r\n','') for x in request.form.getlist('users')]
        output = extract_mails(upload_file_path, users, download_file_path)

        try:
            return send_file(output, as_attachment=True)
        except FileNotFoundError:
            flash('No file created')
            return redirect(request.url_root)

    if 'ch_usr' in list(request.form.keys()):
        ch_usr = request.form['ch_usr']
        usr = request.form['usr'] + '\n'
        if usr == '':
            flash('Введите имя пользователя')
            return redirect(request.url_root)
        if usr not in all_users and ch_usr == 'Удалить':
            flash('Пользователя нет в файле')
            return redirect(request.url_root)
        if usr in all_users and ch_usr == 'Добавить':
            flash('Пользователь уже есть в файле')
            return redirect(request.url_root)
        ch_users(usr,ch_usr)
        return render_template('index.html', users=all_users)