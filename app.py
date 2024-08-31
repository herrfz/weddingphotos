import os
import asyncio
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
from pathlib import PureWindowsPath
from backend.worker import Backup, restore
from psycopg2.extras import RealDictCursor
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session
load_dotenv()


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images')

PASSWORD = os.getenv('PASSWORD')
DATABASE_URL = os.getenv('DATABASE_URL')
event = os.getenv('EVENT')


# Utility function to get a database connection
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn


# Restore media on app restart
asyncio.run(restore(app.config['UPLOAD_FOLDER']))


# Route to handle the main index
@app.route('/', defaults={'username': None, 'task_id': None})
@app.route('/<username>/<int:task_id>')
def index(username, task_id):
    if task_id is not None and task_id != 0 and username is not None:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM tasks WHERE id = %s', (task_id,))
        task = cur.fetchone()
        conn.close()
        if task:
            return render_template('index.html', username=username, task=task)
    return render_template('index.html')


# Route to handle file upload
@app.route('/upload/<username>/<int:task_id>', methods=['POST'])
def upload(username, task_id):
    if 'media' not in request.files:
        return redirect(url_for('index', username=username, task_id=task_id))
    
    file = request.files['media']
    if file.filename == '':
        return redirect(url_for('index', username=username, task_id=task_id))
    
    if file:
        timestamp = datetime.now()
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.mkdir(app.config['UPLOAD_FOLDER'])
        filename = secure_filename(f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        posixfilepath = PureWindowsPath(filepath).as_posix()
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO media(task_id, mediafile, username, taken, event) VALUES (%s, %s, %s, %s, %s)", 
                    (task_id, posixfilepath, username, timestamp, event))
        conn.commit()
        conn.close()

        backup = Backup(filepath)
        backup.start()

        return render_template('uploaded.html', filepath=posixfilepath)

    return redirect(url_for('index', username=username, task_id=task_id))


# Route to handle gallery access
@app.route('/gallery', methods=['GET', 'POST'])
def gallery():
    if request.method == 'POST':
        password = request.form['password']
        if password == PASSWORD:  # Replace with a real password validation
            session['logged_in'] = True
            return redirect(url_for('gallery'))
        else:
            return render_template('login.html', error='Incorrect password.')
    
    if not session.get('logged_in'):
        return render_template('login.html')
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''SELECT media.id, description, mediafile, username, likes, taken 
                FROM media LEFT JOIN tasks
                ON media.task_id = tasks.id
                WHERE media.event = %s AND media.mediafile IS NOT NULL
                ORDER BY taken DESC''', (event,))
    media = cur.fetchall()
    conn.close()

    return render_template('gallery.html', media=media)


# Route to handle likes
@app.route('/like/<int:media_id>', methods=['POST'])
def like(media_id):
    if 'liked_tasks' not in session:
        session['liked_tasks'] = []

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM media WHERE id = %s', (media_id,))
    task = cur.fetchone()

    if media_id in session['liked_tasks']:
        # If the task is already liked, decrement the likes
        cur.execute('UPDATE media SET likes = likes - 1 WHERE id = %s', (media_id,))
        session['liked_tasks'].remove(media_id)
        session.modified = True
    else:
        # If the task is not liked yet, increment the likes
        cur.execute('UPDATE media SET likes = likes + 1 WHERE id = %s', (media_id,))
        session['liked_tasks'].append(media_id)
        session.modified = True

    conn.commit()
    cur.execute('SELECT * FROM media WHERE id = %s', (media_id,))
    updated_task = cur.fetchone()
    conn.close()

    return str(updated_task['likes'])


if __name__ == '__main__':
    app.run(debug=True)
