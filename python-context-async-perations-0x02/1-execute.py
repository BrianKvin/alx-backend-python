'''
Objective: create a reusable context manager that takes a query as input and executes it, managing both connection and the query execution

Instructions:

Implement a class based custom context manager ExecuteQuery that takes the query: ”SELECT * FROM users WHERE age > ?” and the parameter 25 and returns the result of the query

Ensure to use the__enter__() and the __exit__() methods

Repo:

GitHub repository: alx-backend-python
Directory: python-context-async-perations-0x02
File: 1-execute.py
'''

import sqlite3

class ExecuteQuery:
    def __init__(self, db_name, query, params=()):
        self.db_name = db_name
        self.query = query
        self.params = params
        self.conn = None
        self.cursor = None

    def __enter__(self):
        # Open the database connection and create a cursor
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        # Execute the query with the provided parameters
        self.cursor.execute(self.query, self.params)
        # Return the query results
        return self.cursor.fetchall()

    def __exit__(self, exc_type, exc_value, traceback):
        # Commit changes if no exception, rollback otherwise
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        # Close cursor and connection
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

# Example usage
if __name__ == "__main__":
    try:
        query = "SELECT * FROM users WHERE age > ?"
        with ExecuteQuery('users.db', query, (25,)) as results:
            print("Query results:", results)
    except Exception as e:
        print(f"Error: {e}")