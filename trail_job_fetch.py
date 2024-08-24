import sqlite3

DATABASE = 'recruitment.db'

def fetch_jobs():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM job_applications')
    jobs = cursor.fetchall()
    for job in jobs:
        print(job)

fetch_jobs()
