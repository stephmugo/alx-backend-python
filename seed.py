import mysql.connector
from mysql.connector import Error
import uuid
import csv
import os


def connect_db():
    """
    Connects to the MySQL database server
    
    Returns:
        connection: MySQL connection object
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root"
        )
        print("Connected to MySQL Database")
        return connection
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None


def create_database(connection):
    """
    Creates the database ALX_prodev if it does not exist
    
    Args:
        connection: MySQL connection object
    """
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        print("Database ALX_prodev created or already exists")
    except Error as e:
        print(f"Error creating database: {e}")


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
        print("Connected to ALX_prodev Database")
        return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev Database: {e}")
        return None


def create_table(connection):
    """
    Creates a table user_data if it does not exist with the required fields
    
    Args:
        connection: MySQL connection object
    """
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                user_id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                age DECIMAL(5,2) NOT NULL,
                INDEX (user_id)
            )
        """)
        print("Table user_data created or already exists")
    except Error as e:
        print(f"Error creating table: {e}")


def insert_data(connection, data):
    """
    Inserts data in the database if it does not exist
    
    Args:
        connection: MySQL connection object
        data: List of tuples containing user data
    """
    try:
        cursor = connection.cursor()
        
        # First check if record exists
        select_query = "SELECT user_id FROM user_data WHERE user_id = %s"
        insert_query = """
            INSERT INTO user_data (user_id, name, email, age)
            VALUES (%s, %s, %s, %s)
        """
        
        records_inserted = 0
        for record in data:
            # Check if record with this user_id exists
            cursor.execute(select_query, (record[0],))
            if not cursor.fetchone():
                cursor.execute(insert_query, record)
                records_inserted += 1
        
        connection.commit()
        print(f"{records_inserted} records inserted into user_data table")
    except Error as e:
        print(f"Error inserting data: {e}")


def load_csv_data(filename='user_data.csv'):
    """
    Load data from CSV file
    
    Args:
        filename: CSV filename
        
    Returns:
        data: List of tuples containing user data
    """
    data = []
    try:
        with open(filename, 'r') as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader)  # Skip header row
            
            for row in csv_reader:
                if len(row) >= 3:  # Ensure we have at least name, email, age
                    # Generate UUID for user_id
                    user_id = str(uuid.uuid4())
                    name = row[0]
                    email = row[1]
                    age = float(row[2])
                    
                    data.append((user_id, name, email, age))
                    
        print(f"Loaded {len(data)} records from CSV")
        return data
    except Exception as e:
        print(f"Error loading CSV data: {e}")
        return []


if __name__ == "__main__":
    # Connect to MySQL server
    conn = connect_db()
    if conn:
        # Create database
        create_database(conn)
        conn.close()
        
        # Connect to the specific database
        db_conn = connect_to_prodev()
        if db_conn:
            # Create table
            create_table(db_conn)
            
            # Check if CSV file exists
            if os.path.exists('user_data.csv'):
                # Load data from CSV
                csv_data = load_csv_data()
                
                # Insert data into database
                if csv_data:
                    insert_data(db_conn, csv_data)
            else:
                print("Error: user_data.csv file not found")
            
            db_conn.close()