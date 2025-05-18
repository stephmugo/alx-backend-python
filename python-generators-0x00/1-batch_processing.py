#!/usr/bin/env python3
"""
1-batch_processing.py - Stream and process users in batches
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


def stream_users_in_batches(batch_size):
    """
    Generator function that yields batches of rows from the user_data table
    
    Args:
        batch_size: Number of rows to fetch in each batch
        
    Yields:
        list: A batch of rows from the user_data table
    """
    connection = connect_to_prodev()
    
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM user_data")
            
            batch = []
            for row in cursor:
                batch.append(row)
                
                # When batch reaches specified size, yield it
                if len(batch) >= batch_size:
                    yield batch
                    batch = []  # Reset batch
            
            # Yield any remaining rows (last batch may be smaller)
            if batch:
                yield batch
                
        except Error as e:
            print(f"Error streaming users in batches: {e}")
        finally:
            cursor.close()
            connection.close()


def batch_processing(batch_size):
    """
    Process batches of users and filter those over age 25
    
    Args:
        batch_size: Number of rows to fetch in each batch
        
    Yields:
        list: Filtered users over age 25 from the current batch
    """
    # Process each batch
    for batch in stream_users_in_batches(batch_size):
        # Filter users over age 25
        filtered_users = [user for user in batch if float(user[3]) > 25]
        yield filtered_users


if __name__ == "__main__":
    # Example usage
    batch_size = 5  # Process 5 users at a time
    
    print(f"Processing users in batches of {batch_size}, filtering for age > 25:")
    batch_num = 1
    
    for filtered_batch in batch_processing(batch_size):
        print(f"\nBatch {batch_num} results:")
        if filtered_batch:
            for user in filtered_batch:
                user_id, name, email, age = user
                print(f"User: {name}, Email: {email}, Age: {age}")
        else:
            print("No users over age 25 in this batch")
        
        batch_num += 1