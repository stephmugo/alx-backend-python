import time
import sqlite3 
import functools

# Global dictionary to store cached results
query_cache = {}

# Decorator to cache query results based on SQL string
def cache_query(func):
    @functools.wraps(func)
    def wrapper(conn, query, *args, **kwargs):
        if query in query_cache:
            print("🔁 Returning cached result.")
            return query_cache[query]
        else:
            print("🆕 Executing and caching query.")
            result = func(conn, query, *args, **kwargs)
            query_cache[query] = result
            return result
    return wrapper

# Reuse from earlier: Automatically manage DB connections
def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return wrapper

#  Function wrapped with both connection handler and cache
@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#  First call — hits DB and caches result
users = fetch_users_with_cache(query="SELECT * FROM users")

#  Second call — instantly returns cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")
