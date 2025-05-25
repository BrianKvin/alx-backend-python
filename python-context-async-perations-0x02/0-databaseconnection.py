'''
Objective: create a class based context manager to handle opening and closing database connections automatically

Instructions:

Write a class custom context manager DatabaseConnection using the __enter__ and the __exit__ methods

Use the context manager with the with statement to be able to perform the query SELECT * FROM users. Print the results from the query.
'''

import sqlite3

class DatabaseConnection:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def __enter__(self):
        # Open the database connection and create a cursor
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        return self.conn  # Return the connection object for use in the with block

    def __exit__(self, exc_type, exc_value, traceback):
        # Commit changes if no exception occurred, otherwise rollback
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        # Close the cursor and connection
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

# Example usage with the context manager
if __name__ == "__main__":
    try:
        with DatabaseConnection('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
            print("Query results:", results)
    except Exception as e:
        print(f"Error: {e}")