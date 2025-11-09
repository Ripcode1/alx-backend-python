#!/usr/bin/python3
"""
Batch processing module for filtering users by age
"""
import seed


def stream_users_in_batches(batch_size):
    """
    Generator that fetches rows in batches from the database
    
    Args:
        batch_size: Number of rows to fetch per batch
        
    Yields:
        list: Batch of user dictionaries
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data")
    
    batch = []
    for row in cursor:
        batch.append(row)
        if len(batch) == batch_size:
            yield batch
            batch = []
    
    if batch:
        yield batch
    
    cursor.close()
    connection.close()


def batch_processing(batch_size):
    """
    Processes each batch to filter users over the age of 25
    
    Args:
        batch_size: Size of each batch to process
    """
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user['age'] > 25:
                print(user)
                print()
