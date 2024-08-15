from flask import Flask, render_template, request, redirect, url_for, session
import os
import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.mkdir(app.config['UPLOAD_FOLDER'])
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        file_ext = filename.rsplit('.', 1)[1].lower()
        return render_template('uploaded.html', filename=filename, file_ext=file_ext)
    return redirect(url_for('index'))

@app.route('/gallery', methods=['GET', 'POST'])
def gallery():
    if 'authenticated' not in session:
        if request.method == 'POST':
            password = request.form['password']
            if password == 'wedding2024':
                session['authenticated'] = True
                return redirect(url_for('gallery'))
            else:
                error = 'Invalid password, please try again.'
                return render_template('login.html', error=error)
        return render_template('login.html')

    files = os.listdir(app.config['UPLOAD_FOLDER'])
    files = [f for f in files if allowed_file(f)]
    return render_template('gallery.html', files=files)

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return url_for('static', filename=f'images/{filename}')

if __name__ == '__main__':
    app.run(debug=True)
