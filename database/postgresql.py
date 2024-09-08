import asyncpg
from contextlib import asynccontextmanager

TABLE_NAME = 'servers'
DESIRED_SCHEMA = {
    "server_id": "BIGINT PRIMARY KEY",
    "is_setup": "BOOLEAN NOT NULL",
    "debug_channel_id": "BIGINT",  # Use BIGINT for Discord IDs
    "welcome_channel_id": "BIGINT"
}

pool = None

async def create_pool(config):
    global pool
    DATABASE_CONFIG = config['database']['postgresql']
    pool = await asyncpg.create_pool(**DATABASE_CONFIG)

@asynccontextmanager
async def get_db_connection():
    async with pool.acquire() as conn:
        yield conn

async def init_db_postgresql(config):
    async with get_db_connection() as conn:
        # Check if the table exists
        table_exists = await conn.fetchval(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE  table_schema = 'public' 
                AND    table_name   = '{TABLE_NAME}'
            );
        """)

        if not table_exists:
            # Create the table if it doesn't exist
            column_definitions = ", ".join([f"{col_name} {col_type}" for col_name, col_type in DESIRED_SCHEMA.items()])
            await conn.execute(f"CREATE TABLE {TABLE_NAME} ({column_definitions})")
        else:
            # If the table exists, only add missing columns
            existing_columns = await conn.fetch(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{TABLE_NAME}'")
            existing_column_names = {column['column_name'] for column in existing_columns}

            for column_name, column_type in DESIRED_SCHEMA.items():
                if column_name not in existing_column_names:
                    await conn.execute(f'ALTER TABLE {TABLE_NAME} ADD COLUMN {column_name} {column_type}')

async def check_server_setup_postgresql(server_id):
    async with get_db_connection() as conn:
        row = await conn.fetchrow(f'SELECT is_setup FROM {TABLE_NAME} WHERE server_id = $1', server_id)
        return row and row['is_setup']

async def set_server_setup_postgresql(server_id, debug_channel_id):
    async with get_db_connection() as conn:
        await conn.execute(f'''
            INSERT INTO {TABLE_NAME} 
            (server_id, is_setup, debug_channel_id) 
            VALUES ($1, $2, $3)
            ON CONFLICT (server_id) DO UPDATE 
            SET is_setup = $2, debug_channel_id = $3
        ''', server_id, True, debug_channel_id)

async def get_debug_channel_postgresql(server_id):
    async with get_db_connection() as conn:
        row = await conn.fetchrow(f'SELECT debug_channel_id FROM {TABLE_NAME} WHERE server_id = $1', server_id)
        return row and row['debug_channel_id']

async def set_welcome_channel_postgresql(server_id, welcome_channel_id):
    async with get_db_connection() as conn:
        await conn.execute(f'''
            UPDATE {TABLE_NAME} 
            SET welcome_channel_id = $1 
            WHERE server_id = $2
        ''', welcome_channel_id, server_id)

async def get_welcome_channel_postgresql(server_id):
    async with get_db_connection() as conn:
        row = await conn.fetchrow(f'SELECT welcome_channel_id FROM {TABLE_NAME} WHERE server_id = $1', server_id)
        return row and row['welcome_channel_id']