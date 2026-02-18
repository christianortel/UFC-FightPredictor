import sqlite3
import os

DB_NAME = "ufc_data.db"

def get_connection():
    """Returns a connection to the SQLite database."""
    return sqlite3.connect(DB_NAME)

def init_db():
    """Initializes the database with the schema."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Enable foreign key support
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 1. Fighters Table (Biographical Info)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fighters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        nickname TEXT,
        height_cm INTEGER,
        reach_cm INTEGER,
        stance TEXT,
        dob TEXT,
        weight_lbs INTEGER,
        weight_class TEXT,
        url TEXT
    );
    """)
    
    # 2. Stats Table (Performance Metrics)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fighter_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fighter_id INTEGER NOT NULL,
        wins INTEGER,
        losses INTEGER,
        draws INTEGER,
        sapm REAL,
        slpm REAL,
        str_acc REAL,
        str_def REAL,
        td_avg REAL,
        td_acc REAL,
        td_def REAL,
        sub_avg REAL,
        FOREIGN KEY (fighter_id) REFERENCES fighters (id)
    );
    """)
    
    conn.commit()
    conn.close()
    print(f"Database {DB_NAME} initialized successfully.")

if __name__ == "__main__":
    init_db()
