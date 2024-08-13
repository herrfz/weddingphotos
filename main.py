from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Photo Upload</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #f8f9fa;
        }

        .container {
            text-align: center;
            background-color: #fff;
            padding: 30px 50px;
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }

        h1 {
            font-size: 26px;
            color: #343a40;
            margin-bottom: 30px;
        }

        .button {
            display: inline-block;
            margin: 15px 0;
            padding: 15px 30px;
            font-size: 18px;
            color: #fff;
            background-color: #007bff;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.3s ease;
            text-decoration: none;
            width: 100%;
            max-width: 300px;
        }

        .button:hover {
            background-color: #0056b3;
            transform: translateY(-3px);
        }

        .button:active {
            transform: translateY(1px);
        }

        .button + .button {
            margin-top: 10px;
        }

        .button-icon {
            margin-right: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Upload or Take a Photo</h1>

        <!-- Button to open the camera on mobile or webcam on laptop -->
        <button class="button" id="take-photo-button">
            <span class="button-icon">📷</span> Take a Photo
        </button>
        <input type="file" id="camera-input" accept="image/*" capture="camera" style="display:none;" />

        <!-- Button to open the gallery (mobile) or file picker (laptop) -->
        <button class="button" id="choose-photo-button">
            <span class="button-icon">🖼️</span> Choose from Gallery
        </button>
        <input type="file" id="gallery-input" accept="image/*" style="display:none;" />
    </div>

    <script>
        document.getElementById('take-photo-button').addEventListener('click', function() {
            document.getElementById('camera-input').click();
        });

        document.getElementById('choose-photo-button').addEventListener('click', function() {
            document.getElementById('gallery-input').click();
        });

        // Handle file input change (for demo purposes)
        document.getElementById('camera-input').addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                alert(`Camera Photo selected: ${file.name}`);
            }
        });

        document.getElementById('gallery-input').addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                alert(`Gallery Photo selected: ${file.name}`);
            }
        });
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host='0.0.0.0')
