import sqlite3

class ExecuteQuery:
    """Reusable context manager that executes a query and manages connection."""
    
    def __init__(self, db_name, query, params=None):
        self.db_name = db_name
        self.query = query
        self.params = params or ()
        self.connection = None
        self.results = None
    
    def __enter__(self):
        """Enter the context, execute query, and return results."""
        self.connection = sqlite3.connect(self.db_name)
        cursor = self.connection.cursor()
        cursor.execute(self.query, self.params)
        self.results = cursor.fetchall()
        return self.results
    
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
        cursor.execute("INSERT OR REPLACE INTO users (id, name, age) VALUES (4, 'Diana', 35)")
        cursor.execute("INSERT OR REPLACE INTO users (id, name, age) VALUES (5, 'Eve', 28)")
        conn.commit()
    
    # Use the ExecuteQuery context manager with the specified query
    query = "SELECT * FROM users WHERE age > ?"
    parameter = (25,)
    
    with ExecuteQuery("example.db", query, parameter) as results:
        print("Users older than 25:")
        for row in results:
            print(f"ID: {row[0]}, Name: {row[1]}, Age: {row[2]}")