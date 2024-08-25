from flask import Flask, render_template, request, redirect, url_for, session, send_file
import sqlite3
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import shutil

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key
app.config['UPLOAD_FOLDER'] = 'static/images/'
PASSWORD = '1234'
event = 'oma'  # TODO: encode in URLs and QR code

# Ensure the images directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Utility function to get a database connection
def get_db_connection():
    conn = sqlite3.connect('db.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

# Route to handle the main index
@app.route('/', defaults={'user': None, 'task_id': None})
@app.route('/<user>/<int:task_id>')
def index(user, task_id):
    if task_id is not None and task_id != 0 and user is not None:
        conn = get_db_connection()
        task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
        conn.close()
        if task:
            return render_template('index.html', user=user, task=task)
    return render_template('index.html')

# Route to handle file upload
@app.route('/upload/<user>/<int:task_id>', methods=['POST'])
def upload(user, task_id):
    if 'media' not in request.files:
        return redirect(url_for('index', user=user, task_id=task_id))
    
    file = request.files['media']
    if file.filename == '':
        return redirect(url_for('index', user=user, task_id=task_id))
    
    if file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.mkdir(app.config['UPLOAD_FOLDER'])
        filename = secure_filename(f"{timestamp}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        conn = get_db_connection()
        conn.execute('''INSERT INTO media(task_id, media, user, taken, event) 
                     VALUES (?, ?, ?, ?, ?)''', (task_id, filepath, user, timestamp, event))
        conn.commit()
        conn.close()

        return render_template('uploaded.html', filepath=filepath)

    return redirect(url_for('index', user=user, task_id=task_id))

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
    media = conn.execute('''SELECT media.id, description, media, user, likes 
                         FROM media LEFT JOIN tasks 
                         ON media.task_id = tasks.id 
                         WHERE media.event = ? AND media.media IS NOT NULL''', (event,)).fetchall()
    conn.close()

    return render_template('gallery.html', media=media)

# Route to handle likes
@app.route('/like/<int:media_id>', methods=['POST'])
def like(media_id):
    if 'liked_tasks' not in session:
        session['liked_tasks'] = []

    conn = get_db_connection()
    task = conn.execute('SELECT * FROM media WHERE id = ?', (media_id,)).fetchone()

    if media_id in session['liked_tasks']:
        # If the task is already liked, decrement the likes
        conn.execute('UPDATE media SET likes = likes - 1 WHERE id = ?', (media_id,))
        session['liked_tasks'].remove(media_id)
        session.modified = True
    else:
        # If the task is not liked yet, increment the likes
        conn.execute('UPDATE media SET likes = likes + 1 WHERE id = ?', (media_id,))
        session['liked_tasks'].append(media_id)
        session.modified = True

    conn.commit()
    updated_task = conn.execute('SELECT * FROM media WHERE id = ?', (media_id,)).fetchone()
    conn.close()

    return str(updated_task['likes'])

# allow downloading database
@app.route('/download', defaults={'images': None})
@app.route('/download/<int:images>')
def downloadFile (images):
    dbpath = "db.sqlite"
    mediapath = "media.zip"
    if images == 0:
        archive = shutil.make_archive(mediapath, 'zip', app.config['UPLOAD_FOLDER'])
        return send_file(archive, as_attachment=True)
    else:
        return send_file(dbpath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
