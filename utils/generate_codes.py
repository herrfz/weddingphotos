import os
import docx
import segno
import psycopg2
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(dotenv_path=(Path(__file__).parents[1] / '.env'))
from itertools import cycle
from psycopg2.extras import RealDictCursor
from docx.enum.table import WD_ALIGN_VERTICAL


DATABASE_URL = os.getenv('DATABASE_URL')
event = os.getenv('EVENT')
BASEURL = 'https://weddingphotos-243848a36014.herokuapp.com'
DOCNAME = event + '_tasks.docx'

tasks = None
users = None
doc = docx.Document()
table = doc.add_table(rows=0, cols=2)


try:
    with psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor) as conn:
        cur = conn.cursor()
        cur.execute('SELECT id, description FROM tasks WHERE event = %s', (event,))
        tasks = cur.fetchall()

        cur = conn.cursor()
        cur.execute('SELECT name FROM users')
        users = cur.fetchall()

except Exception as e:
    print(e)

if users is not None and tasks is not None:
    for user, task in zip(users, cycle(tasks)):
        taskid = str(task['id'])
        taskurl = '/'.join([BASEURL, user['name'], taskid])
        print(taskurl)

        qrcode = segno.make_qr(taskurl)
        filename = user['name'] + '_' + taskid + '.png'
        qrcode.save(filename, scale=3, border=3)

        cells = table.add_row().cells
        # add image to first column
        par = cells[0].add_paragraph()
        run = par.add_run()
        run.add_picture(filename)
        # add description to second column
        cells[1].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        cells[1].text = task['description']

    doc.save(DOCNAME)
