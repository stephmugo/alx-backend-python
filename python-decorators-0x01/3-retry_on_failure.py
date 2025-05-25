import time
import sqlite3
import functools

# Reuse connection handler from Task 1
def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            result = func(conn, *args, **kwargs)
        finally:
            conn.close()
        return result
    return wrapper

# Retry decorator for handling transient errors
def retry_on_failure(retries=3, delay=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Attempt {attempt} failed: {e}")
                    last_exception = e
                    if attempt < retries:
                        time.sleep(delay)  # wait before retrying
            # After all retries, re-raise the last exception
            raise last_exception
        return wrapper
    return decorator

# Function to fetch users with automatic retries on failure
@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

# Attempt to fetch users
users = fetch_users_with_retry()
print(users)
