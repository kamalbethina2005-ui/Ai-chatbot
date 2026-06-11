import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def init_db():
    db_path = os.path.join(BASE_DIR, 'medical_chatbot.db')
    schema_path = os.path.join(BASE_DIR, 'schema.sql')
    conn = sqlite3.connect(db_path)
    with open(schema_path, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.close()
    print("Database initialized from schema.sql.")

if __name__ == '__main__':
    init_db()
