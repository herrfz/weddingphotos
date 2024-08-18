from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key
app.config['UPLOAD_FOLDER'] = 'static/images/'

# Ensure the images directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Utility function to get a database connection
def get_db_connection():
    conn = sqlite3.connect('db.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

# Route to handle the main index
@app.route('/', defaults={'task_id': None})
@app.route('/<int:task_id>')
def index(task_id):
    if task_id is not None and task_id != 0:
        conn = get_db_connection()
        task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
        conn.close()
        if task:
            return render_template('index.html', task=task)
    return render_template('index.html')

# Route to handle file upload
@app.route('/upload/<int:task_id>', methods=['POST'])
def upload(task_id):
    if 'media' not in request.files:
        return redirect(url_for('index', task_id=task_id))
    
    file = request.files['media']
    if file.filename == '':
        return redirect(url_for('index', task_id=task_id))
    
    if file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.mkdir(app.config['UPLOAD_FOLDER'])
        filename = secure_filename(f"{timestamp}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        conn = get_db_connection()
        if task_id == 0:
            conn.execute('INSERT INTO tasks(media, taken) VALUES (?, ?)', (filepath, timestamp))
        else:
            conn.execute('UPDATE tasks SET media = ?, taken = ? WHERE id = ?', (filepath, timestamp, task_id))
        conn.commit()
        conn.close()

        return render_template('uploaded.html', filepath=filepath)

    return redirect(url_for('index', task_id=task_id))

# Route to handle gallery access
@app.route('/gallery', methods=['GET', 'POST'])
def gallery():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'your_password':  # Replace with a real password validation
            session['logged_in'] = True
            return redirect(url_for('gallery'))
        else:
            return render_template('login.html', error='Incorrect password.')
    
    if not session.get('logged_in'):
        return render_template('login.html')
    
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks WHERE media IS NOT NULL').fetchall()
    conn.close()

    return render_template('gallery.html', tasks=tasks)

# Route to handle likes
@app.route('/like/<int:task_id>', methods=['POST'])
def like(task_id):
    conn = get_db_connection()
    conn.execute('UPDATE tasks SET likes = likes + 1 WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
