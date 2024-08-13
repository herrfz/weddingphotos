from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key for security

# Configurations
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['PASSWORD'] = 'your_password'  # Set a password for the gallery

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

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
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Pass filename to the result page
        return render_template('result.html', filename=filename)

    return redirect(request.url)

@app.route('/gallery', methods=['GET', 'POST'])
def gallery():
    if request.method == 'POST':
        password = request.form['password']
        if password == app.config['PASSWORD']:
            session['authenticated'] = True
            return redirect(url_for('show_gallery'))
        else:
            flash('Incorrect password. Please try again.')
    
    return render_template('password.html')

@app.route('/show_gallery')
def show_gallery():
    if not session.get('authenticated'):
        return redirect(url_for('gallery'))
    
    images = os.listdir(app.config['UPLOAD_FOLDER'])
    image_urls = [os.path.join('uploads/', img) for img in images]
    return render_template('gallery.html', images=image_urls)

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('gallery'))

if __name__ == '__main__':
    app.run(debug=True)
