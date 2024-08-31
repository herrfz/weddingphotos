import os
import dropbox
import asyncio
import psycopg2
import threading
from pathlib import Path, PureWindowsPath
from dotenv import load_dotenv
load_dotenv(dotenv_path=(Path(__file__).parents[1] / '.env'))
from psycopg2.extras import RealDictCursor


DATABASE_URL = os.getenv('DATABASE_URL')
DROPBOX_ACCESS_TOKEN = os.getenv('DROPBOX_ACCESS_TOKEN')
event = os.getenv('EVENT')


class Backup(threading.Thread):
    def __init__(self, filepath):
        threading.Thread.__init__(self, daemon=True)
        self.filepath = filepath

    def run(self):
        try:
            posixfilepath = PureWindowsPath(self.filepath).as_posix()
            dbxfilename = '/' + event + '/' + posixfilepath
            
            dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
            with open(self.filepath, 'rb') as f:
                dbx.files_upload(f.read(), dbxfilename)

            conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
            cur = conn.cursor()
            cur.execute('UPDATE media SET cloudurl = %s WHERE mediafile = %s',
                        (dbxfilename, posixfilepath))
            conn.commit()
            conn.close()

        except Exception as e:
            print(e)


def _fetch(url, save_as):
    try:
        dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
        with open(save_as, 'wb') as file:
            _, response = dbx.files_download(url)
            file.write(response.content)
    except Exception as e:
        print(e)


async def restore(download_folder):
    if not os.path.exists(download_folder):
        os.mkdir(download_folder)

    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    cur = conn.cursor()
    cur.execute('SELECT * FROM media WHERE event = %s AND mediafile IS NOT NULL', (event,))
    media = cur.fetchall()
    conn.commit()
    conn.close()

    tasks = []

    for med in media:
        tasks.append(asyncio.to_thread(_fetch, med['cloudurl'], med['mediafile']))

    await asyncio.gather(*tasks)
