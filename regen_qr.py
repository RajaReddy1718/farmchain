import os
import sqlite3
from dotenv import load_dotenv
from qr_generator import generate_qr

load_dotenv()
base_url = os.getenv('VERIFY_BASE_URL')
if not base_url:
    raise SystemExit('VERIFY_BASE_URL is not set in .env')

base_url = base_url.rstrip('/')
if not base_url.endswith('/verify'):
    base_url += '/verify'

conn = sqlite3.connect('farmchain.db')
cur = conn.cursor()
cur.execute('SELECT batch_id FROM batches')
rows = cur.fetchall()
print(f'Regenerating {len(rows)} QR code(s) using {base_url}/<batch_id>')
for row in rows:
    batch_id = row[0]
    verify_url = f'{base_url}/{batch_id}'
    path = generate_qr(batch_id, verify_url)
    print('WROTE', path)
conn.close()
