import sqlite3
import os

def setup_database():
    print("Setting up SQLite database...")
    
    # Connect to the local SQLite file (it will be created if it doesn't exist)
    conn = sqlite3.connect('noid_db.sqlite')
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        pid TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT,
        year TEXT,
        program TEXT,
        dob TEXT
    )
    """)
    
    # Create Access Log table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS access_log (
        pid TEXT PRIMARY KEY,
        access_count INTEGER DEFAULT 0,
        last_generated_time TEXT,
        week_number INTEGER,
        FOREIGN KEY (pid) REFERENCES users(pid)
    )
    """)
    
    # Insert Sample Data (using INSERT OR REPLACE for SQLite)
    sample_users = [
        ('PID123', 'John Doe', 'Computer Science', '2024', 'B.Tech', '2000-01-15'),
        ('PID456', 'Jane Smith', 'Information Tech', '2025', 'B.Tech', '2001-05-20')
    ]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO users (pid, name, department, year, program, dob) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, sample_users)
    
    conn.commit()
    conn.close()
    print("Database setup completed successfully! The local 'noid_db.sqlite' file has been created.")

if __name__ == '__main__':
    setup_database()
