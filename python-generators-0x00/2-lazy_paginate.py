#!/usr/bin/python3
"""
Lazy pagination module for fetching paginated data
"""
import seed


def paginate_users(page_size, offset):
    """
    Fetches a page of users from the database
    
    Args:
        page_size: Number of users per page
        offset: Starting position for the page
        
    Returns:
        list: List of user dictionaries for the page
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    connection.close()
    return rows


def lazy_pagination(page_size):
    """
    Generator that lazily loads pages of users
    
    Args:
        page_size: Number of users per page
        
    Yields:
        list: Page of user dictionaries
    """
    offset = 0
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size
