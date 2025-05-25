'''
Objective: create a decorator that retries database operations if they fail due to transient errors

Instructions:

Complete the script below by implementing a retry_on_failure(retries=3, delay=2) decorator that retries the function of a certain number of times if it raises an exception
import time
import sqlite3 
import functools

#### paste your with_db_decorator here

""" your code goes here"""

@with_db_connection
@retry_on_failure(retries=3, delay=1)

def fetch_users_with_retry(conn):
cursor = conn.cursor()
cursor.execute("SELECT * FROM users")
return cursor.fetchall()

#### attempt to fetch users with automatic retry on failure

users = fetch_users_with_retry()
print(users)
'''

import sqlite3
import functools
import time

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

def retry_on_failure(retries=3, delay=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            while attempt <= retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == retries:
                        raise  # Re-raise the last exception if max retries reached
                    print(f"Attempt {attempt} failed with error: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    attempt += 1
        return wrapper
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

# Example usage
if __name__ == "__main__":
    try:
        users = fetch_users_with_retry()
        print(users)
    except Exception as e:
        print(f"Error after retries: {e}")