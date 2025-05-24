'''
Objective: create a generator that streams rows from an SQL database one by one.

Instructions:

Write a python script that seed.py:

Set up the MySQL database, ALX_prodev with the table user_data with the following fields:
user_id(Primary Key, UUID, Indexed)
name (VARCHAR, NOT NULL)
email (VARCHAR, NOT NULL)
age (DECIMAL,NOT NULL)
Populate the database with the sample data from this user_data.csv
Prototypes:
def connect_db() :- connects to the mysql database server
def create_database(connection):- creates the database ALX_prodev if it does not exist
def connect_to_prodev() connects the the ALX_prodev database in MYSQL
def create_table(connection):- creates a table user_data if it does not exists with the required fields
def insert_data(connection, data):- inserts data in the database if it does not exist
'''
# pip install mysql-connector-python

#!/usr/bin/python3
import mysql.connector
import csv
import uuid

def connect_db():
    """
    Connects to the MySQL database server.
    Returns a connection object or None if connection fails.
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # Replace with your MySQL username
            password=""   # Replace with your MySQL password
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

def create_database(connection):
    """
    Creates the ALX_prodev database if it does not exist.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")

def connect_to_prodev():
    """
    Connects to the ALX_prodev database.
    Returns a connection object or None if connection fails.
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # Replace with your MySQL username
            password="",  # Replace with your MySQL password
            database="ALX_prodev"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to ALX_prodev: {err}")
        return None

def create_table(connection):
    """
    Creates the user_data table if it does not exist.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                user_id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                age DECIMAL(5,2) NOT NULL,
                INDEX idx_user_id (user_id)
            )
        """)
        connection.commit()
        print("Table user_data created successfully")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error creating table: {err}")

def insert_data(connection, data):
    """
    Inserts data from the provided CSV file into the user_data table if it does not exist.
    """
    try:
        cursor = connection.cursor()
        with open(data, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # Skip header row if present
            for row in csv_reader:
                # Generate UUID if not provided in CSV
                user_id = str(uuid.uuid4()) if len(row) < 4 else row[0]
                name = row[1] if len(row) > 1 else row[0]
                email = row[2] if len(row) > 2 else row[1]
                age = float(row[3] if len(row) > 3 else row[2])
                
                # Check if user_id already exists
                cursor.execute("SELECT user_id FROM user_data WHERE user_id = %s", (user_id,))
                if cursor.fetchone() is None:
                    cursor.execute("""
                        INSERT INTO user_data (user_id, name, email, age)
                        VALUES (%s, %s, %s, %s)
                    """, (user_id, name, email, age))
        connection.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error inserting data: {err}")
    except FileNotFoundError:
        print(f"CSV file {data} not found")
    except Exception as e:
        print(f"Error processing CSV data: {e}")

if __name__ == "__main__":
    # Example usage
    connection = connect_db()
    if connection:
        create_database(connection)
        connection.close()
        
        connection = connect_to_prodev()
        if connection:
            create_table(connection)
            insert_data(connection, 'user_data.csv')
            connection.close()