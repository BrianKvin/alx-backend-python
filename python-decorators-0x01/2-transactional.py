'''
Objective: create a decorator that manages database transactions by automatically committing or rolling back changes

Instructions:

Complete the script below by writing a decorator transactional(func) that ensures a function running a database operation is wrapped inside a transaction.If the function raises an error, rollback; otherwise commit the transaction.

Copy the with_db_connection created in the previous task into the script

import sqlite3 
import functools

"""your code goes here"""

@with_db_connection 
@transactional 
def update_user_email(conn, user_id, new_email): 
cursor = conn.cursor() 
cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id)) 
#### Update user's email with automatic transaction handling 

update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
'''

import sqlite3
import functools

def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            result = func(conn, *args, **kwargs)
            return result
        except Exception as e:
            raise
        finally:
            conn.close()
    return wrapper

def transactional(func):
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            # Execute the function
            result = func(conn, *args, **kwargs)
            # Commit the transaction if no errors
            conn.commit()
            return result
        except Exception as e:
            # Rollback the transaction on error
            conn.rollback()
            raise
    return wrapper

@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))

# Example usage
if __name__ == "__main__":
    try:
        update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
        print("User email updated successfully")
    except Exception as e:
        print(f"Error: {e}")