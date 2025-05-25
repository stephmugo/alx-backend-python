import time
import sqlite3 
import functools
import logging
from typing import Tuple, List, Dict, Callable

# Conf logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

query_cache: Dict[str, Tuple[List[Tuple], float]] = {}

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


def cache_query(func: Callable) -> Callable:
    
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        query = kwargs.get('query')
        if not query:
            if args and isinstance(args[0], str):
                query = args[0]
            else:
                logger.warning("No query provided for caching")
                return func(conn, *args, **kwargs)
        
        cache_key = query
        
        if cache_key in query_cache:
            cached_result, timestamp = query_cache[cache_key]
            cache_age = time.time() - timestamp
            logger.info(f"Cache hit for query: {query[:50]}... (Age: {cache_age:.2f}s)")
            return cached_result
        
        logger.info(f"Cache miss for query: {query[:50]}...")
        start_time = time.time()
        result = func(conn, *args, **kwargs)
        execution_time = time.time() - start_time
        
        query_cache[cache_key] = (result, time.time())
        
        logger.info(f"Query executed in {execution_time:.4f}s and cached")
        return result
    
    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
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
        (2, "Spencer James", "james@example.com"),
    ]
    
    for user in test_users:
        cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (?, ?, ?)", user)
    
    conn.commit()
    conn.close()
    
    print("1. First call will execute the query and cache the result:")
    start_time = time.time()
    users = fetch_users_with_cache(query="SELECT * FROM users")
    first_call_time = time.time() - start_time
    print(f"   Result: {users}")
    print(f"   Execution time: {first_call_time:.6f} seconds")
    
    print("\n2. Second call with the same query will use the cached result:")
    start_time = time.time()
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    second_call_time = time.time() - start_time
    print(f"   Result: {users_again}")
    print(f"   Execution time: {second_call_time:.6f} seconds")
    print(f"   Speed improvement: {first_call_time / second_call_time:.2f}x faster")
    
    print("\n3. Different query will not use the cache:")
    start_time = time.time()
    filtered_users = fetch_users_with_cache(query="SELECT * FROM users WHERE id = 1")
    print(f"   Result: {filtered_users}")
    print(f"   Execution time: {time.time() - start_time:.6f} seconds")