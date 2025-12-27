import asyncpg
import asyncio
import os
from dotenv import load_dotenv

async def test_db():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    print(f"Testing connection to: {db_url}")
    
    try:
        conn = await asyncpg.connect(db_url)
        print("✅ Connection successful!")
        
        # Check current user
        user = await conn.fetchval("SELECT current_user")
        print(f"Current DB User: {user}")
        
        # Check schema permissions
        try:
            await conn.execute("CREATE TABLE IF NOT EXISTS test_perm (id SERIAL PRIMARY KEY)")
            await conn.execute("DROP TABLE test_perm")
            print("✅ Permission to CREATE tables confirmed!")
        except Exception as perm_err:
            print(f"❌ Permission error: {perm_err}")
            
        await conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_db())
