'''
0. Logging database Queries

Objective: create a decorator that logs database queries executed by any function

Instructions:

Complete the code below by writing a decorator log_queries that logs the SQL query before executing it.

Prototype: def log_queries()

import sqlite3
import functools

#### decorator to lof SQL queries

 """ YOUR CODE GOES HERE"""

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")
'''

import sqlite3
import functools
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_queries(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get the query from the first argument
        query = args[0] if args else "No query provided"
        logging.info(f"Executing query: {query}")
        
        try:
            result = func(*args, **kwargs)
            logging.info(f"Query executed successfully")
            return result
        except Exception as e:
            logging.error(f"Query failed: {str(e)}")
            raise
    
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Example usage
if __name__ == "__main__":
    try:
        users = fetch_all_users(query="SELECT * FROM users")
        print(users)
    except Exception as e:
        print(f"Error: {e}")