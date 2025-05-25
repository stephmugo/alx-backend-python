import sqlite3

class DatabaseConnection:
    """Custom context manager for handling database connections."""
    
    def __init__(self, db_name="example.db"):
        self.db_name = db_name
        self.connection = None
    
    def __enter__(self):
        """Enter the context and return the database connection."""
        self.connection = sqlite3.connect(self.db_name)
        return self.connection
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the context and close the database connection."""
        if self.connection:
            if exc_type is None:
                # Commit if no exception occurred
                self.connection.commit()
            else:
                # Rollback if an exception occurred
                self.connection.rollback()
            self.connection.close()
        
        # Return False to propagate any exceptions
        return False

# Example 
if __name__ == "__main__":
    # First, let's create a sample database with users table
    with sqlite3.connect("example.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                         (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)''')
        cursor.execute("INSERT OR REPLACE INTO users (id, name, age) VALUES (1, 'Alice', 30)")
        cursor.execute("INSERT OR REPLACE INTO users (id, name, age) VALUES (2, 'Bob', 25)")
        cursor.execute("INSERT OR REPLACE INTO users (id, name, age) VALUES (3, 'Charlie', 45)")
        conn.commit()
    
    # Now use our custom context manager
    with DatabaseConnection("example.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        
        print("Query results:")
        for row in results:
            print(f"ID: {row[0]}, Name: {row[1]}, Age: {row[2]}")