import sqlite3

DATABASE = 'recruitment.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            skills TEXT NOT NULL
        );
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            position TEXT NOT NULL,
            company TEXT NOT NULL,
            FOREIGN KEY(username) REFERENCES users(username)
        );
        ''')
        conn.commit()
    print("Database initialized and table created.")

def update_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Check if columns already exist to avoid re-adding them
        cursor.execute("PRAGMA table_info(users);")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'name' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN name TEXT NOT NULL DEFAULT ""')
        if 'email' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN email TEXT NOT NULL DEFAULT ""')
        if 'skills' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN skills TEXT NOT NULL DEFAULT ""')
        
        conn.commit()
    print("Database updated with new columns.")

def verify_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(users);")
        columns = [info[1] for info in cursor.fetchall()]
        print("Users table columns:", columns)

if __name__ == '__main__':
    init_db()
    update_db()
    verify_db()
