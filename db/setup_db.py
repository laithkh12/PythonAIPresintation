import os
import sqlite3

# Create the db folder if it doesn't exist
if not os.path.exists('db'):
    os.makedirs('db')

# Path to the SQLite database file
db_path = os.path.join('db', 'uploads.db')

# Connect to the SQLite database (it will be created if it doesn't exist)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create Users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL
)
''')

# Create Uploads table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Uploads (
    id INTEGER PRIMARY KEY,
    uid TEXT NOT NULL,
    filename TEXT NOT NULL,
    upload_time TEXT NOT NULL,
    finish_time TEXT,
    status TEXT NOT NULL,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES Users (id)
)
''')

# Commit changes and close the connection
conn.commit()
conn.close()

print(f"Database created at {db_path}")
