#!/usr/bin/env python3
"""
0-stream_users.py - Generator that streams rows from an SQL database one by one
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


def stream_users():
    """
    Generator function that yields rows from the user_data table one by one
    
    Yields:
        tuple: A single row from the user_data table
    """
    connection = connect_to_prodev()
    
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM user_data")
            
            # Yield each row one by one
            for row in cursor:
                yield row
                
        except Error as e:
            print(f"Error streaming users: {e}")
        finally:
            cursor.close()
            connection.close()


if __name__ == "__main__":
    # Example usage
    print("Streaming users one by one:")
    for user in stream_users():
        user_id, name, email, age = user
        print(f"User: {name}, Email: {email}, Age: {age}")