import asyncio
import aiosqlite
import sqlite3

async def async_fetch_users():
    """Asynchronously fetch all users from the database."""
    async with aiosqlite.connect("example.db") as db:
        cursor = await db.execute("SELECT * FROM users")
        results = await cursor.fetchall()
        return results

async def async_fetch_older_users():
    """Asynchronously fetch users older than 40 from the database."""
    async with aiosqlite.connect("example.db") as db:
        cursor = await db.execute("SELECT * FROM users WHERE age > ?", (40,))
        results = await cursor.fetchall()
        return results

async def fetch_concurrently():
    """Execute both queries concurrently using asyncio.gather."""
    # Run both queries concurrently
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    
    print("All users:")
    for row in all_users:
        print(f"ID: {row[0]}, Name: {row[1]}, Age: {row[2]}")
    
    print("\nUsers older than 40:")
    for row in older_users:
        print(f"ID: {row[0]}, Name: {row[1]}, Age: {row[2]}")

# Setup function to create sample data
def setup_database():
    """Create sample database with users table."""
    with sqlite3.connect("example.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                         (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)''')
        cursor.execute("INSERT OR REPLACE INTO users (id, name, age) VALUES (1, 'Alice', 30)")
        cursor.execute("INSERT OR REPLACE INTO users (id, name, age) VALUES (2, 'Bob', 25)")
        cursor.execute("INSERT OR REPLACE INTO users (id, name, age) VALUES (3, 'Charlie', 45)")
        cursor.execute("INSERT OR REPLACE INTO users (id, name, age) VALUES (4, 'Diana', 35)")
        cursor.execute("INSERT OR REPLACE INTO users (id, name, age) VALUES (5, 'Eve', 42)")
        cursor.execute("INSERT OR REPLACE INTO users (id, name, age) VALUES (6, 'Frank', 50)")
        conn.commit()

# Main execution
if __name__ == "__main__":
    # Setup the database first
    setup_database()
    
    # Run the concurrent fetch
    asyncio.run(fetch_concurrently())