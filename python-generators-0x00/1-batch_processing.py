#!/usr/bin/python3
"""
Batch processing module for filtering users by age
"""
import seed


def streamusersinbatches(batchsize):
    """
    Generator that fetches rows in batches from the database
    
    Args:
        batchsize: Number of rows to fetch per batch
        
    Yields:
        list: Batch of user dictionaries
    """
    connection = seed.connect_to_prodev()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")
        
        batch = []
        for row in cursor:
            batch.append(row)
            if len(batch) == batchsize:
                yield batch
                batch = []
        
        if batch:
            yield batch
        
        cursor.close()
        connection.close()


def batch_processing(batchsize):
    """
    Processes each batch to filter users over the age of 25
    
    Args:
        batchsize: Size of each batch to process
    """
    for batch in streamusersinbatches(batchsize):
        for user in batch:
            if user['age'] > 25:
                print(user)
