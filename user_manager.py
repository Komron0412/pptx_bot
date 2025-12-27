
import asyncpg
import json
import os
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class UserManager:
    """Manages user data persistence using PostgreSQL with JSON fallback"""
    
    def __init__(self, db_url: Optional[str] = None, json_path="users.json"):
        self.db_url = db_url or os.getenv("DATABASE_URL")
        self.json_path = json_path
        self.users_cache: Dict[str, dict] = {}
        self.pool = None
        
    async def init(self):
        """Initialize database connection or load JSON"""
        if self.db_url:
            try:
                # Use a local variable first to avoid race conditions with get_user
                pool = await asyncpg.create_pool(self.db_url)
                async with pool.acquire() as conn:
                    # Create tables one by one for better reliability
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS users (
                            user_id BIGINT PRIMARY KEY,
                            data JSONB NOT NULL
                        )
                    ''')
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS presentations (
                            id SERIAL PRIMARY KEY,
                            user_id BIGINT,
                            topic TEXT NOT NULL,
                            template TEXT,
                            slide_count INTEGER,
                            language TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    await conn.execute('CREATE INDEX IF NOT EXISTS idx_pres_user ON presentations(user_id)')
                
                # Assign pool to self after tables are guaranteed to exist
                self.pool = pool
                logger.info("Connected to PostgreSQL database and verified tables")
                
                # Try to migrate from JSON if needed
                await self._migrate_from_json()
                return
            except Exception as e:
                logger.error(f"Failed to connect to PostgreSQL or create tables: {e}. Falling back to JSON.")
        
        self._load_json()

    def _load_json(self):
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    self.users_cache = json.load(f)
                logger.info(f"Loaded {len(self.users_cache)} users from JSON")
            except Exception as e:
                logger.error(f"Error loading JSON users: {e}")

    async def get_user(self, user_id: int) -> Optional[dict]:
        """Get user data by ID (Async)"""
        if self.pool:
            try:
                async with self.pool.acquire() as conn:
                    row = await conn.fetchrow('SELECT data FROM users WHERE user_id = $1', user_id)
                    return json.loads(row['data']) if row else None
            except Exception as e:
                logger.error(f"DB Error in get_user: {e}")
        
        return self.users_cache.get(str(user_id))

    async def save_user(self, user_id: int, data: dict):
        """Save or update user data (Async)"""
        # Update local cache for safety/fast access if DB dies
        str_id = str(user_id)
        if str_id not in self.users_cache:
            self.users_cache[str_id] = {}
        self.users_cache[str_id].update(data)
        
        if self.pool:
            try:
                # Merge existing data in DB
                existing = await self.get_user(user_id) or {}
                existing.update(data)
                json_data = json.dumps(existing)
                
                async with self.pool.acquire() as conn:
                    await conn.execute('''
                        INSERT INTO users (user_id, data) 
                        VALUES ($1, $2)
                        ON CONFLICT (user_id) 
                        DO UPDATE SET data = $2
                    ''', user_id, json_data)
                return
            except Exception as e:
                logger.error(f"DB Error in save_user: {e}")
        
        # Fallback to JSON saving
        self._save_json()

    async def save_presentation(self, user_id: int, topic: str, template: str, slide_count: int, language: str):
        """Record a successful presentation generation"""
        if self.pool:
            try:
                async with self.pool.acquire() as conn:
                    await conn.execute('''
                        INSERT INTO presentations (user_id, topic, template, slide_count, language)
                        VALUES ($1, $2, $3, $4, $5)
                    ''', user_id, topic, template, slide_count, language)
                logger.info(f"Recorded presentation for user {user_id}")
            except Exception as e:
                logger.error(f"DB Error in save_presentation: {e}")

    async def get_history(self, user_id: int, limit: int = 5):
        """Get recent presentation history for a user"""
        if self.pool:
            try:
                async with self.pool.acquire() as conn:
                    rows = await conn.fetch('''
                        SELECT topic, template, created_at 
                        FROM presentations 
                        WHERE user_id = $1 
                        ORDER BY created_at DESC 
                        LIMIT $2
                    ''', user_id, limit)
                    return rows
            except Exception as e:
                logger.error(f"DB Error in get_history: {e}")
        return []

    async def _migrate_from_json(self):
        """Migrate data from JSON to PostgreSQL if DB is empty"""
        if not self.pool:
            return
            
        try:
            async with self.pool.acquire() as conn:
                count = await conn.fetchval('SELECT COUNT(*) FROM users')
                if count == 0 and os.path.exists(self.json_path):
                    self._load_json()
                    if self.users_cache:
                        logger.info(f"Migrating {len(self.users_cache)} users from JSON to PostgreSQL...")
                        for user_id_str, data in self.users_cache.items():
                            user_id = int(user_id_str)
                            json_data = json.dumps(data)
                            await conn.execute('''
                                INSERT INTO users (user_id, data) 
                                VALUES ($1, $2)
                                ON CONFLICT (user_id) DO UPDATE SET data = $2
                            ''', user_id, json_data)
                        logger.info("Migration complete!")
        except Exception as e:
            logger.error(f"Error during migration: {e}")

    def _save_json(self):
        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(self.users_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving JSON users: {e}")

