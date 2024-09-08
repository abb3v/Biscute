import aiosqlite
from contextlib import asynccontextmanager

TABLE_NAME = 'servers'
DESIRED_SCHEMA = {
    "server_id": "INTEGER PRIMARY KEY",  # SQLite uses INTEGER for primary keys
    "is_setup": "BOOLEAN NOT NULL",
    "debug_channel_id": "INTEGER",
    "welcome_channel_id": "INTEGER"
}

pool = None

async def create_pool(config):
    global pool
    DATABASE_CONFIG = config['database']['sqlite']
    pool = await aiosqlite.connect(DATABASE_CONFIG["filename"])
    await pool.execute("PRAGMA foreign_keys = ON")

@asynccontextmanager
async def get_db_connection():
    global pool
    yield pool

async def init_db_sqlite(config):
    async with get_db_connection() as conn:
        # Check if the table exists
        cursor = await conn.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{TABLE_NAME}'")
        table_exists = await cursor.fetchone() is not None

        if not table_exists:
            # Create the table if it doesn't exist
            column_definitions = ", ".join([f"{col_name} {col_type}" for col_name, col_type in DESIRED_SCHEMA.items()])
            await conn.execute(f"CREATE TABLE {TABLE_NAME} ({column_definitions})")
        else:
            # If the table exists, only add missing columns
            cursor = await conn.execute(f"PRAGMA table_info({TABLE_NAME})")
            existing_column_names = {row[1] for row in await cursor.fetchall()}

            for column_name, column_type in DESIRED_SCHEMA.items():
                if column_name not in existing_column_names:
                    await conn.execute(f'ALTER TABLE {TABLE_NAME} ADD COLUMN {column_name} {column_type}')
        # Commit the changes
        await conn.commit()

async def check_server_setup_sqlite(server_id):
    async with get_db_connection() as conn:
        cursor = await conn.execute(f'SELECT is_setup FROM {TABLE_NAME} WHERE server_id = ?', (server_id,))
        row = await cursor.fetchone()
        return row and row[0]

async def set_server_setup_sqlite(server_id, debug_channel_id):
    async with get_db_connection() as conn:
        await conn.execute(f'''
            INSERT INTO {TABLE_NAME} 
            (server_id, is_setup, debug_channel_id) 
            VALUES (?, ?, ?)
            ON CONFLICT (server_id) DO UPDATE 
            SET is_setup = ?, debug_channel_id = ?
        ''', (server_id, True, debug_channel_id, True, debug_channel_id))
        await conn.commit()

async def get_debug_channel_sqlite(server_id):
    async with get_db_connection() as conn:
        cursor = await conn.execute(f'SELECT debug_channel_id FROM {TABLE_NAME} WHERE server_id = ?', (server_id,))
        row = await cursor.fetchone()
        return row and row[0]

async def set_welcome_channel_sqlite(server_id, welcome_channel_id):
    async with get_db_connection() as conn:
        await conn.execute(f'''
            UPDATE {TABLE_NAME} 
            SET welcome_channel_id = ? 
            WHERE server_id = ?
        ''', (welcome_channel_id, server_id))
        await conn.commit()

async def get_welcome_channel_sqlite(server_id):
    async with get_db_connection() as conn:
        cursor = await conn.execute(f'SELECT welcome_channel_id FROM {TABLE_NAME} WHERE server_id = ?', (server_id,))
        row = await cursor.fetchone()
        return row and row[0]