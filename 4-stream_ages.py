#!/usr/bin/env python3
"""
4-stream_ages.py - Memory-efficient aggregation using generators
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


def stream_user_ages():
    """
    Generator function that yields user ages one by one
    
    Yields:
        float: Age of a user
    """
    connection = connect_to_prodev()
    
    if connection:
        try:
            cursor = connection.cursor()
            # We only need the age column (index 3)
            cursor.execute("SELECT age FROM user_data")
            
            # Yield each age one by one
            for row in cursor:
                yield float(row[0])  # Convert to float to ensure proper calculation
                
        except Error as e:
            print(f"Error streaming user ages: {e}")
        finally:
            cursor.close()
            connection.close()


def calculate_average_age():
    """
    Calculate average age without loading entire dataset into memory
    
    Returns:
        float: Average age of all users
    """
    total_age = 0
    count = 0
    
    # Process each age one by one
    for age in stream_user_ages():
        total_age += age
        count += 1
    
    # Avoid division by zero
    if count == 0:
        return 0
    
    return total_age / count


if __name__ == "__main__":
    # Calculate and print average age
    avg_age = calculate_average_age()
    print(f"Average age of users: {avg_age:.2f}")