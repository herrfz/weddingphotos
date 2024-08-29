import os
import queue
import psycopg2
import threading
from pathlib import Path, PureWindowsPath
from dotenv import load_dotenv
load_dotenv(dotenv_path=(Path(__file__).parents[1] / '.env'))
import cloudinary
import cloudinary.uploader
from watchdog.observers import Observer
from psycopg2.extras import RealDictCursor
from watchdog.events import FileSystemEventHandler



DATABASE_URL = os.getenv('DATABASE_URL')


class _EventHandler(FileSystemEventHandler):
    def __init__(self, queue, *args, **kwargs):
        self._queue = queue
        super(*args, **kwargs)

    def on_created(self, event):
        try:
            self._queue.put(event.src_path, timeout=5)
        except queue.Full:
            print('ERROR: cannot put into task queue')


class Uploader(threading.Thread):
    def __init__(self, path, recursive):
        threading.Thread.__init__(self, daemon=True)
        self.queue = queue.Queue()
        handler = _EventHandler(self.queue)
        observer = Observer()
        observer.schedule(handler, path, recursive=recursive)
        observer.start()
        print("Observer started")

    def run(self):
        while True:
            try:
                filepath = self.queue.get(timeout=5)
                posixfilepath = PureWindowsPath(filepath).as_posix()
                upload_result = cloudinary.uploader.upload(filepath)

                conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
                cur = conn.cursor()
                cur.execute('UPDATE media SET cloudurl = %s WHERE mediafile = %s',
                             (upload_result['secure_url'], posixfilepath))
                conn.commit()
                conn.close()

            except KeyboardInterrupt:
                break

            except queue.Empty:
                continue

            except Exception as e:
                print(e)
                continue
