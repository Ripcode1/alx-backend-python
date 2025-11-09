#!/usr/bin/python3
"""
Generator function to stream rows from the user_data table
"""
import seed


def stream_users():
    """
    Generator that yields user rows one by one from the database
    
    Yields:
        dict: User data as a dictionary
    """
    connection = seed.connect_to_prodev()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")
        
        for row in cursor:
            yield row
        
        cursor.close()
        connection.close()
