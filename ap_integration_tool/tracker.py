import sqlite3
import time
import pandas as pd

DB_FILE = "jobs.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS file_uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            status TEXT,
            rows INTEGER,
            uploaded_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_file_upload(filename, status, rows):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO file_uploads (filename, status, rows, uploaded_at) VALUES (?, ?, ?, ?)",
              (filename, status, rows, time.strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_file_uploads():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM file_uploads ORDER BY id DESC", conn)
    conn.close()
    return df