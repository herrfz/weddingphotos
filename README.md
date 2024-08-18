Prompt 

```
You are a professional web developer, full stack developer, web and UI UX designer with decades of experience. Please create a Flask web application with the following specifications:
- The app shall consist of the file app.py, and a folder called templates containing the files index.html, uploaded.html, login.html, gallery.html.
- There shall be a folder called static that contains the file style.css and a subfolder called images.
- There shall be an sqlite database file called db.sqlite
- The database shall have one table called tasks, with the following fields:
	- id: integer, index of the table
	- description: text 
	- media: text
	- taken: timestamp
	- likes: integer
- The app shall not create or initialize the database.
- The main file index.html shall be callable without parameter or with a route parameter with the task id in the database as a parameter.
- If the index.html is called without a parameter, it shall show a text "Take a photo or video!", and it shall show a button, which when pressed, offers the user to capture a photo, capture a video, or select a photo or video from the user's photo gallery app.
- If the index.html is called with a parameter, it shall show a text "Your task is: " followed by the description of the task in the same text style, corresponding to the id on the URL parameter, and a button, which when pressed, offers the user to capture a photo, capture a video, or select a photo or video from the user's photo gallery app.
- If the user chooses to capture a photo or video, the app shall open the camera app and allow the user to capture a photo or video. If the user chooses to select a photo or video, the app shall open the photo gallery app and allow the user to select a photo or video.
- When the user has captured or select a photo or video, the app shall automatically rename the photo and video to include a timestamp and store the photo or video in the static/images folder. The app shall check if the folder static/images exist and create the folder if it does not exist. If the photo or video has a task id, update the database media field for the task with the path to the photo or video, and the taken field for the task with the timestamp. The app shall then show the upload.html page with a preview of the photo or video. The upload.html page shall also provide a button to go to the gallery.html.
- If the user chooses to open the gallery.html page, the app shall show the login.html page asking for a password.
- If the user provides the correct password, the app shall show the gallery.html page. The user shall only be required to enter the password once within a session.
- The gallery.html page shall show the uploaded photos or videos in the database. Under each photo or video, the description corresponding to the id of the photo or video in the database shall be shown. Next to the description there shall be a heart icon and the number of likes. If the heart icon is clicked, it shall show a small animation, and the app shall increment the likes value of the photo or video in the database and on the page.  The photos or videos shall be shown centered, maintaining its aspect ratio. The gallery.html page shall allow user to scroll up or down to view each photo or video. At the top of the gallery.html page there shall be a link to go back to the main index.html file without parameter.
- The app shall be functional both in mobile and desktop web browsers.
- The app's buttons, style and theme shall be sleek, nice, and professional, coherent across all pages, with subtle colors suitable for a wedding, and with subtle transparency, subtle color gradient backgrounds. The color of the buttons shall be in harmony with the background color.
- The app shall support photo and video formats from Apple iPhone and Android phones.
```

Mods
```
- use linear-gradient(to bottom, rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.7)) as theme
- only one button on index.html, shall provide the menu to take a photo or video, or select a photo or video from gallery
- when the user presses like, the like count shall be updated in real time, you may use htmx for that
- the like button shall show only the heart icon, no background button shape, the style of the heart shall be like the one from Instagram

- On the index.html page, once the user captures or selects a photo or video, the app shall automatically upload
- Please adapt the color theme for the buttons to match the background theme better
- Please fit the preview size on the uploaded.html page to fit the screen
- Please adapt the uploaded.html to provide a button to go to gallery

- When the user presses the heart icon multiple times, the app shall alternately increment or decrement the likes count. This is to ensure that liking can be done only once.

- The heart icon returns a json string after clicked, can you fix that to show still the heart icon with the likes count?
- Please add a subtle gray line under each media on the gallery.html page, and make the description text more visually appealing, like better fonts and slightly bold
```

Manual fixes
```
session.modified = True
```