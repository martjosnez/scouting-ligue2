import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "scouting.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()
    conn.close()
    print(f"Base initialisée : {DB_PATH}")

if __name__ == "__main__":
    init_db()