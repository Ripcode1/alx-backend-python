#!/usr/bin/python3
"""
Memory-efficient age aggregation using generators
"""
import seed


def stream_user_ages():
    """
    Generator that yields user ages one by one
    
    Yields:
        int: User age
    """
    connection = seed.connect_to_prodev()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT age FROM user_data")
        
        for row in cursor:
            yield row[0]
        
        cursor.close()
        connection.close()


def calculate_average_age():
    """
    Calculates the average age of users using a generator
    without loading the entire dataset into memory
    """
    total_age = 0
    count = 0
    
    for age in stream_user_ages():
        total_age += age
        count += 1
    
    if count > 0:
        average_age = total_age / count
        print(f"Average age of users: {average_age:.2f}")
    else:
        print("No users found in database")


if __name__ == "__main__":
    calculate_average_age()
