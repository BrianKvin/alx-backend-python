'''
Objective: Run multiple database queries concurrently using asyncio.gather.

Instructions:

Use the aiosqlite library to interact with SQLite asynchronously. To learn more about it, click here.

Write two asynchronous functions: async_fetch_users() and async_fetch_older_users() that fetches all users and users older than 40 respectively.

Use the asyncio.gather() to execute both queries concurrently.

Use asyncio.run(fetch_concurrently()) to run the concurrent fetch
'''

import asyncio
import aiosqlite

async def async_fetch_users():
    async with aiosqlite.connect('users.db') as conn:
        cursor = await conn.execute("SELECT * FROM users")
        results = await cursor.fetchall()
        await cursor.close()
        return results

async def async_fetch_older_users():
    async with aiosqlite.connect('users.db') as conn:
        cursor = await conn.execute("SELECT * FROM users WHERE age > ?", (40,))
        results = await cursor.fetchall()
        await cursor.close()
        return results

async def fetch_concurrently():
    # Run both queries concurrently using asyncio.gather
    users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    return users, older_users

# Example usage
if __name__ == "__main__":
    try:
        # Run the concurrent fetch
        results = asyncio.run(fetch_concurrently())
        users, older_users = results
        print("All users:", users)
        print("Users older than 40:", older_users)
    except Exception as e:
        print(f"Error: {e}")