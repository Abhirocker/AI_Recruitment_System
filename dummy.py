import sqlite3

DATABASE = 'recruitment.db'

def check_job_applications_table():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(job_applications);")
        columns = [info[1] for info in cursor.fetchall()]
        print("job_applications table columns:", columns)

        if 'username' not in columns:
            cursor.execute('ALTER TABLE job_applications ADD COLUMN username TEXT')
            conn.commit()
            print("Username column added to job_applications table.")

check_job_applications_table()