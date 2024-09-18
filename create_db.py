import sqlite3
from datetime import datetime

DATABASE = 'recruitment.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn
        
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        
        # Drop the old table
        # cursor.execute('DROP TABLE IF EXISTS users;')
        
        # Create users table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                skills Text,
                last_position TEXT,
                education TEXT,
                achievements TEXT,
                certifications TEXT,
                location TEXT,
                experience TEXT,
                is_admin BOOLEAN NOT NULL DEFAULT 0
            );
        ''')
        
        # Create job_applications table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                position TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT NOT NULL,
                experience_range TEXT NOT NULL,
                description TEXT NOT NULL,
                posted_date TEXT NOT NULL
            );
        ''')
        
        # Create a table for storing selected candidates
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS selected_candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                employee_id TEXT NOT NULL UNIQUE,
                job_title TEXT NOT NULL,
                date_of_joining TEXT NOT NULL,
                position TEXT NOT NULL
            )
        ''')
        
        # Fetch user_application table
        create_user_applications_table()

        # Insert predefined admin user if it doesn't already exist
        admin_username = 'admin'
        admin_password = 'admin_123'  # Direct password storage
        cursor.execute('SELECT * FROM users WHERE username = ?', (admin_username,))
        admin_exists = cursor.fetchone()
            
        if not admin_exists:
            cursor.execute('''
            INSERT INTO users (username, password, name, email, is_admin)
            VALUES (?, ?, ?, ?, ?)
            ''', (admin_username, admin_password, 'Admin', 'admin@lazy.com', 1))

    conn.commit()
print("Database initialized and table created.")

def create_user_applications_table():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                job_id INTEGER NOT NULL,
                resume TEXT,
                application_date TEXT,
                similarity_score FLOAT,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (job_id) REFERENCES job_applications(id)
            )
        ''')
        conn.commit()

def update_db():
    drop_tables()
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        
        # Update the user table
        # Check if columns already exist to avoid re-adding them
        cursor.execute("PRAGMA table_info(users);")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'name' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0 ""')
        if 'email' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN email TEXT NOT NULL DEFAULT ""')
        if 'skills' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN skills TEXT NOT NULL DEFAULT ""')
        if 'is_admin' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0')
        if 'last_position' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN last_position TEXT NOT NULL DEFAULT ""')
        if 'education' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN education TEXT NOT NULL DEFAULT ""')
        if 'achievements' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN achievements TEXT ""')
        if 'certifications' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN certifications TEXT ""')
        if 'location' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN location TEXT NOT NULL DEFAULT ""')
        if 'experience' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN experience TEXT NOT NULL DEFAULT ""')
        
        # Update the 'job_application' table
        cursor.execute("PRAGMA table_info(job_applications);")
        job_columns = [info[1] for info in cursor.fetchall()]
        
        if 'location' not in job_columns:
            cursor.execute('ALTER TABLE job_applications ADD COLUMN location TEXT NOT NULL DEFAULT ""')
        if 'experience_range' not in job_columns:
            cursor.execute('ALTER TABLE job_applications ADD COLUMN experience_range TEXT NOT NULL DEFAULT ""')
        if 'description' not in job_columns:
            cursor.execute('ALTER TABLE job_applications ADD COLUMN description TEXT NOT NULL DEFAULT ""')
        if 'posted_date' not in job_columns:
            cursor.execute('ALTER TABLE job_applications ADD COLUMN posted_date TEXT NOT NULL DEFAULT ""')
        
        conn.commit()
    print("Database updated with new columns.")

def verify_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(users);")
        columns = [info[1] for info in cursor.fetchall()]
        print("Users table columns:", columns)

def add_job_application(position, company, location, experience_range, description):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        posted_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
        INSERT INTO job_applications (position, company, location, experience_range, description, posted_date)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (position, company, location, experience_range, description, posted_date))
        conn.commit()

def update_job_application(app_id, position, company, location, experience_range, description, posted_date=None):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        if posted_date is None:
            posted_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Default to current time if not provided
        cursor.execute('''
        UPDATE job_applications
        SET position = ?, company = ?, location = ?, experience_range = ?, description = ?, posted_date = ?
        WHERE id = ?
        ''', (position, company, location, experience_range, description, posted_date, app_id))
        conn.commit()

def delete_job_application(app_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        DELETE FROM job_applications
        WHERE id = ?
        ''', (app_id,))
        conn.commit()

def drop_tables():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS users;')
        cursor.execute('DROP TABLE IF EXISTS job_applications;')
        cursor.execute('DROP TABLE IF EXISTS user_applications;')
        conn.commit()
    print("Tables dropped.")

if __name__ == '__main__':
    init_db()
    update_db()
    verify_db()
    drop_tables()