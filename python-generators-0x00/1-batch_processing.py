#!/usr/bin/python3

import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

def stream_users_in_batches(batch_size):
    try:
        with mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            ) as connection:
            print('Successfully connected to the MySQL server.')

            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM user_data")
                batch = []
                for row in cursor:
                    batch.append(row)
                    if len(batch) == batch_size:
                        yield batch
                        batch = []

            if batch:
                yield batch

    except mysql.connector.Error as e:
        print(f"Database error: {e}")


def batch_processing(batch_size):
    """
    Processes all batches, filters users over age 25, and returns a single combined list.
    """
    all_filtered_users = []  # This will hold everything

    for batch in stream_users_in_batches(batch_size):  # Get each batch from the generator
        filtered = [user for user in batch if float(user.get('age', 0)) > 25]
        all_filtered_users.extend(filtered)  # Add filtered users to the final list

    return all_filtered_users
