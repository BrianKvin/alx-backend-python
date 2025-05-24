#!/usr/bin/python3
#!/usr/bin/python3
import mysql.connector
from seed import connect_to_prodev

def stream_users_in_batches(batch_size):
    """
    Generator function to fetch rows from user_data table in batches.
    Args:
        batch_size (int): Number of rows per batch.
    Yields:
        List of dictionaries representing rows in each batch.
    """
    try:
        connection = connect_to_prodev()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM user_data")
            # Loop 1: Fetch rows in batches
            while True:
                rows = cursor.fetchmany(batch_size)
                if not rows:
                    break
                yield rows
            cursor.close()
            connection.close()
    except mysql.connector.Error as err:
        print(f"Error streaming batches: {err}")

def batch_processing(batch_size):
    """
    Processes batches of users, filtering those over 25 years old.
    Args:
        batch_size (int): Number of rows per batch.
    """
    try:
        # Loop 2: Iterate over batches from the generator
        for batch in stream_users_in_batches(batch_size):
            # Loop 3: Filter users in the batch
            for user in batch:
                if user['age'] > 25:
                    print(user)
    except Exception as err:
        print(f"Error processing batches: {err}")