import os
import asyncio
import requests
import psycopg2
import threading
from pathlib import Path, PureWindowsPath
from dotenv import load_dotenv
load_dotenv(dotenv_path=(Path(__file__).parents[1] / '.env'))
import cloudinary
import cloudinary.uploader
from psycopg2.extras import RealDictCursor


DATABASE_URL = os.getenv('DATABASE_URL')
event = os.getenv('EVENT')


class Backup(threading.Thread):
    def __init__(self, filepath):
        threading.Thread.__init__(self, daemon=True)
        self.filepath = filepath

    def run(self):
        try:
            posixfilepath = PureWindowsPath(self.filepath).as_posix()
            if posixfilepath.lower().endswith(('png', 'jpg', 'jpeg', 'gif')):
                resource_type = 'image'
            elif posixfilepath.lower().endswith(('mp4', 'mov', 'avi')):
                resource_type = 'video'
            else:
                resource_type= 'auto'
            upload_result = cloudinary.uploader.upload(self.filepath, resource_type=resource_type)

            conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
            cur = conn.cursor()
            cur.execute('UPDATE media SET cloudurl = %s WHERE mediafile = %s',
                        (upload_result['secure_url'], posixfilepath))
            conn.commit()
            conn.close()

        except Exception as e:
            print(e)


def _fetch(url, save_as):
    try:
        response = requests.get(url)
        with open(save_as, 'wb') as file:
            file.write(response.content)
    except Exception as e:
        print(e)


async def restore(download_folder):
    if not os.path.exists(download_folder):
        os.mkdir(download_folder)

    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    cur = conn.cursor()
    cur.execute('SELECT * FROM media WHERE event = %s AND mediafile IS NOT NULL', ('oma',))
    media = cur.fetchall()
    conn.commit()
    conn.close()

    tasks = []

    for med in media:
        tasks.append(asyncio.to_thread(_fetch, med['cloudurl'], med['mediafile']))

    await asyncio.gather(*tasks)
