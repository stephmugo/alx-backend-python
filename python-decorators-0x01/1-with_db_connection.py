import sqlite3
import functools

# Decorator to handle DB connections automatically
def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open the connection
        conn = sqlite3.connect('users.db')
        try:
            # Pass the connection to the original function
            result = func(conn, *args, **kwargs)
        finally:
            # Always close the connection, even if there's an error
            conn.close()
        return result
    return wrapper

@with_db_connection
def get_user_by_id(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

# Using the decorated function
user = get_user_by_id(user_id=1)
print(user)
