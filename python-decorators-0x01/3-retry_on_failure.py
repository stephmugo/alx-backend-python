import time
import sqlite3 
import functools
import logging
from typing import Callable, Any, Optional

# Conf logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def with_db_connection(func: Callable) -> Callable:
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            result = func(conn, *args, **kwargs)
            return result
        finally:
            conn.close()
    
    return wrapper


def retry_on_failure(retries: int = 3, delay: int = 2) -> Callable:
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempts = 0
            last_exception: Optional[Exception] = None
            
            while attempts <= retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    last_exception = e
                    
                    if attempts <= retries:
                        logger.warning(
                            f"Attempt {attempts}/{retries} failed for {func.__name__}: {str(e)}"
                            f" - Retrying in {delay} seconds..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {retries} retries failed for {func.__name__}: {str(e)}"
                        )
                        raise last_exception
        
        return wrapper
    return decorator


@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()


# function that simulate database errors
@with_db_connection
@retry_on_failure(retries=3, delay=1)
def simulate_transient_failure(conn):
    if not hasattr(simulate_transient_failure, "attempts"):
        simulate_transient_failure.attempts = 0
    
    simulate_transient_failure.attempts += 1
    
    if simulate_transient_failure.attempts <= 2:
        raise sqlite3.OperationalError("Simulated transient error: database is locked")
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()


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
    
    test_users = [
        (1, "John Doe", "johndoe@example.com"),
        (2, "Spencer James", "james@example.com")
    ]
    
    for user in test_users:
        cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (?, ?, ?)", user)
    
    conn.commit()
    conn.close()
    
    print("1. Regular fetch without simulated errors:")
    users = fetch_users_with_retry()
    print(users)
    
    print("\n2. Fetch with simulated transient errors:")
    print("   (This should retry and succeed after 2 failures)")
    users = simulate_transient_failure()
    print(f"   Success on 3rd attempt: {users}")