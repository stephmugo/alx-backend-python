import sqlite3 
import functools
from typing import Callable, Any

def with_db_connection(func: Callable) -> Callable:
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open a database connection
        conn = sqlite3.connect('users.db')
        
        try:
            # Pass the connection as the first argument
            result = func(conn, *args, **kwargs)
            return result
        finally:
            # Ensure the connection is closed even if an exception occurs
            conn.close()
    
    return wrapper


def transactional(func: Callable) -> Callable:
    
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            # Execute the function within a transaction
            result = func(conn, *args, **kwargs)
            
            # If no exception occurs, commit the transaction
            conn.commit()
            return result
        except Exception as e:
            # If an exception occurs, roll back the transaction
            conn.rollback()
            # Re-raise the exception to be handled by the caller
            raise e
    
    return wrapper


@with_db_connection 
@transactional 
def update_user_email(conn, user_id, new_email): 
    cursor = conn.cursor() 
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))


if __name__ == "__main__":
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL
    )
    ''')
    
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (?, ?, ?)", 
                  (1, "John Doe", "johndoe@example.com"))
    conn.commit()
    
    cursor.execute("SELECT email FROM users WHERE id = ?", (1,))
    print(f"Current email: {cursor.fetchone()[0]}")
    conn.close()
    
    # Update email with automaticaly
    update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM users WHERE id = ?", (1,))
    print(f"Updated email: {cursor.fetchone()[0]}")
    conn.close()