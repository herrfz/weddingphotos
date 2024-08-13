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
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #f0f0f0;
        }

        .container {
            text-align: center;
            background-color: #fff;
            padding: 20px 40px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }

        h1 {
            font-size: 24px;
            color: #333;
            margin-bottom: 20px;
        }

        .button {
            display: inline-block;
            margin: 10px 0;
            padding: 12px 25px;
            font-size: 16px;
            color: #fff;
            background-color: #007BFF;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s ease;
            text-decoration: none;
        }

        .button:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Upload or Take a Photo</h1>

        <!-- Button to open the camera on mobile or webcam on laptop -->
        <form>
            <button class="button" hx-get="#" type="submit" onclick="document.getElementById('camera-input').click(); return false;">📷 Take a Photo</button>
            <input type="file" id="camera-input" accept="image/*" style="display:none;" 
                   capture="environment" hx-post="/upload" hx-trigger="change" hx-swap="none" />
        </form>

        <!-- Button to open the gallery (mobile) or file picker (laptop) -->
        <form>
            <button class="button" hx-get="#" type="submit" onclick="document.getElementById('gallery-input').click(); return false;">🖼️ Choose from Gallery</button>
            <input type="file" id="gallery-input" accept="image/*" style="display:none;" 
                   hx-post="/upload" hx-trigger="change" hx-swap="none" />
        </form>
    </div>

    <script src="https://unpkg.com/htmx.org@1.9.5"></script>
</body>
</html>"""

if __name__ == "__main__":
    app.run(host='0.0.0.0')