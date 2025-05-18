#!/usr/bin/env python3
"""
2-lazy_paginate.py - Lazy loading of paginated data using generators
"""
import mysql.connector
from mysql.connector import Error


def connect_to_prodev():
    """
    Connects to the ALX_prodev database in MySQL
    
    Returns:
        connection: MySQL connection object to ALX_prodev database
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="ALX_prodev"
        )
        return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev Database: {e}")
        return None


def paginate_users(page_size, offset):
    """
    Fetch a single page of users at specified offset
    
    Args:
        page_size: Number of rows per page
        offset: Starting position for fetching rows
        
    Returns:
        list: A list of rows representing one page of data
    """
    connection = connect_to_prodev()
    results = []
    
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT * FROM user_data LIMIT %s OFFSET %s"
            cursor.execute(query, (page_size, offset))
            results = cursor.fetchall()
        except Error as e:
            print(f"Error paginating users: {e}")
        finally:
            cursor.close()
            connection.close()
            
    return results


def lazy_paginate(page_size):
    """
    Generator function that lazily loads pages of data only when needed
    
    Args:
        page_size: Number of rows per page
        
    Yields:
        list: A page of rows from the user_data table
    """
    current_offset = 0
    
    while True:
        # Fetch page at current offset
        page_data = paginate_users(page_size, current_offset)
        
        # If no more data, stop iteration
        if not page_data:
            break
            
        # Yield the current page
        yield page_data
        
        # Move to next page
        current_offset += page_size


if __name__ == "__main__":
    # Example usage
    page_size = 5  # 5 users per page
    
    print(f"Lazily loading paginated data with page size {page_size}:")
    
    page_num = 1
    for page in lazy_paginate(page_size):
        print(f"\nPage {page_num}:")
        
        for user in page:
            user_id, name, email, age = user
            print(f"User: {name}, Email: {email}, Age: {age}")
            
        page_num += 1
        
        # For demonstration purposes, ask if user wants to load next page
        if page_num > 3:  # Automatically stop after 3 pages for this demo
            print("\nDemo: Stopping after 3 pages")
            break
        else:
            print("\nDemo: Loading next page...")