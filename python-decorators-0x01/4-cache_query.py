'''
Objective: create a decorator that caches the results of a database queries inorder to avoid redundant calls

Instructions:

Complete the code below by implementing a decorator cache_query(func) that caches query results based on the SQL query string
import time
import sqlite3 
import functools


query_cache = {}

"""your code goes here"""

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")
'''
import sqlite3
import functools
import time

query_cache = {}

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

def cache_query(func):
    @functools.wraps(func)
    def wrapper(conn, query, *args, **kwargs):
        # Use the query string as the cache key
        if query in query_cache:
            print(f"Returning cached result for query: {query}")
            return query_cache[query]
        
        # Execute the query if not cached
        result = func(conn, query, *args, **kwargs)
        # Store the result in the cache
        query_cache[query] = result
        print(f"Caching result for query: {query}")
        return result
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# Example usage
if __name__ == "__main__":
    try:
        # First call will cache the result
        users = fetch_users_with_cache(query="SELECT * FROM users")
        print("First call result:", users)

        # Second call will use the cached result
        users_again = fetch_users_with_cache(query="SELECT * FROM users")
        print("Second call result:", users_again)
    except Exception as e:
        print(f"Error: {e}")