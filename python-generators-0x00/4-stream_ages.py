#!/usr/bin/python3
import mysql.connector
from seed import connect_to_prodev

def stream_user_ages():
    """
    Generator function to yield user ages one by one from the user_data table.
    Yields:
        Float representing the age of a user.
    """
    try:
        connection = connect_to_prodev()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT age FROM user_data")
            # Loop 1: Yield ages one by one
            for row in cursor:
                yield float(row['age'])
            cursor.close()
            connection.close()
    except mysql.connector.Error as err:
        print(f"Error streaming ages: {err}")

def calculate_average_age():
    """
    Calculates the average age of users using the stream_user_ages generator.
    Prints: Average age of users: <average_age>
    """
    try:
        total_age = 0
        count = 0
        # Loop 2: Iterate over ages from the generator
        for age in stream_user_ages():
            total_age += age
            count += 1
        if count > 0:
            average_age = total_age / count
            print(f"Average age of users: {average_age:.2f}")
        else:
            print("Average age of users: 0.00 (no users found)")
    except Exception as err:
        print(f"Error calculating average age: {err}")

if __name__ == "__main__":
    calculate_average_age()