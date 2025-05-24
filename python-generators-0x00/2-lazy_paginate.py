#!/usr/bin/python3
import mysql.connector
from seed import connect_to_prodev

def paginate_users(page_size, offset):
    """
    Fetches a page of users from the user_data table.
    Args:
        page_size (int): Number of rows per page.
        offset (int): Starting point for the page.
    Returns:
        List of dictionaries containing user data for the page.
    """
    try:
        connection = connect_to_prodev()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
        rows = cursor.fetchall()
        connection.close()
        return rows
    except mysql.connector.Error as err:
        print(f"Error fetching page: {err}")
        return []

def lazy_paginate(page_size):
    """
    Generator function to lazily load pages of users from the user_data table.
    Args:
        page_size (int): Number of rows per page.
    Yields:
        List of dictionaries representing a page of users.
    """
    try:
        offset = 0
        # Single loop to fetch pages
        while True:
            page = paginate_users(page_size, offset)
            if not page:  # Stop if no more data
                break
            yield page
            offset += page_size
    except Exception as err:
        print(f"Error in lazy pagination: {err}")