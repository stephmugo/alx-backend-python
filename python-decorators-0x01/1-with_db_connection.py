import sqlite3 
import functools
from typing import Callable, Any


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


@with_db_connection 
def get_user_by_id(conn, user_id): 
    cursor = conn.cursor() 
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)) 
    return cursor.fetchone() 


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
                  (1, "John Doe", "john@example.com"))
    conn.commit()
    conn.close()
    

    user = get_user_by_id(user_id=1)
    print(user)