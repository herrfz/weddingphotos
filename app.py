from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'static/images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect('db.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', defaults={'task_id': None})
@app.route('/<int:task_id>')
def index(task_id):
    if task_id:
        conn = get_db_connection()
        task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
        conn.close()
        return render_template('index.html', task=task)
    return render_template('index.html', task=None)

@app.route('/upload/<int:task_id>', methods=['POST'])
def upload(task_id):
    if 'file' not in request.files:
        return redirect(url_for('index', task_id=task_id))
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return redirect(url_for('index', task_id=task_id))
    
    filename = secure_filename(file.filename)
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.mkdir(app.config['UPLOAD_FOLDER'])
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    conn = get_db_connection()
    conn.execute('UPDATE tasks SET media = ?, taken = ? WHERE id = ?', 
                 (filename, datetime.now(), task_id))
    conn.commit()
    conn.close()
    
    return render_template('uploaded.html', media_url=url_for('static', filename='images/' + filename))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'your_password':
            session['logged_in'] = True
            return redirect(url_for('gallery'))
        else:
            return render_template('login.html', error='Incorrect password.')
    return render_template('login.html')

@app.route('/gallery')
def gallery():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    media_files = conn.execute('SELECT media FROM tasks WHERE media IS NOT NULL').fetchall()
    conn.close()
    
    return render_template('gallery.html', media_files=media_files)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
