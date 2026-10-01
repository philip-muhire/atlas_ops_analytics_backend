import sqlite3
from pathlib import Path

DB_PATH = Path("saas_analytics.db")
SCHEMA_PATH = Path("schema.sql")

def init_db():
    if DB_PATH.exists():
        DB_PATH.unlink()  # Reset database for clean initial execution

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(SCHEMA_PATH, "r") as f:
        schema_sql = f.read()

    cursor.executescript(schema_sql)
    conn.commit()

    # Verify tables created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    print("Database initialized successfully!")
    print(f"Created Tables: {', '.join(tables)}")
    conn.close()

if __name__ == "__main__":
    init_db()
