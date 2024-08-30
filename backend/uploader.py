import os
import psycopg2
import threading
from pathlib import Path, PureWindowsPath
from dotenv import load_dotenv
load_dotenv(dotenv_path=(Path(__file__).parents[1] / '.env'))
import cloudinary
import cloudinary.uploader
from psycopg2.extras import RealDictCursor


DATABASE_URL = os.getenv('DATABASE_URL')


class Uploader(threading.Thread):
    def __init__(self, filepath):
        threading.Thread.__init__(self, daemon=True)
        self.filepath = filepath

    def run(self):
        while True:
            try:
                posixfilepath = PureWindowsPath(self.filepath).as_posix()
                upload_result = cloudinary.uploader.upload(self.filepath)

                conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
                cur = conn.cursor()
                cur.execute('UPDATE media SET cloudurl = %s WHERE mediafile = %s',
                             (upload_result['secure_url'], posixfilepath))
                conn.commit()
                conn.close()

            except KeyboardInterrupt:
                break

            except Exception as e:
                print(e)
                continue
