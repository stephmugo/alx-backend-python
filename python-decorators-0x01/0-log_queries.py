import sqlite3
import functools
from datetime import datetime

#### decorator to log SQL queries

def log_queries(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if args:
            query = args[0] if isinstance(args[0], str) else None
        elif 'query' in kwargs:
            query = kwargs['query']
        else:
            query = None
        
        if query:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Executing SQL Query: {query}")
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] No SQL query found to log")
        
        return func(*args, **kwargs)
    
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")