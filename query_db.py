# import sqlite3

# def query_database():
#     # Connect to the SQLite database
#     conn = sqlite3.connect('recruitment.db')
#     cursor = conn.cursor()

#     # Execute a query to fetch all records from the users table
#     cursor.execute('SELECT * FROM users')
#     rows = cursor.fetchall()

#     # Print the fetched records
#     for row in rows:
#         print(row)

#     # Close the connection
#     conn.close()

# if __name__ == '__main__':
#     query_database()
