import sqlite3
import os
from pathlib import Path
base = Path(__file__).resolve().parent
db_path = base / 'backend' / 'instance' / 'fyp.db'
print('DB path:', db_path)
print('exists:', db_path.exists())
if db_path.exists():
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    try:
        cur.execute("PRAGMA table_info('project_proposal')")
        rows = cur.fetchall()
        print('project_proposal columns:')
        for row in rows:
            print(row)
    except Exception as e:
        print('ERROR querying table schema:', e)
    finally:
        con.close()
