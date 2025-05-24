#!/user/bin/python3
import mysql.connector
from seed import connect_to_pro_dev

def stream_user():
  ''' In 0-stream_users.py write a function that uses a generator to fetch rows one by one from the user_data table. You must use the Yield python generator
    Prototype: def stream_users()
    Your function should have no more than 1 loop
  '''
  try:
    connection = connect_to_prodev()
    if connection:
      cursor = connection.cursor(dictionary=True)
      # single loop to yield rows one by one
      from row in cursor:
        yield row
        cursor.close()
        connection.close()
  except mysql.connector.Error as err:
    print(f"Error streaming data: {err}")

