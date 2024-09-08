from contextlib import asynccontextmanager
from config import config

pool = None

async def create_pool():
    global pool
    db_type = config['database']['type']
    if db_type == 'postgresql':
        from .postgresql import create_pool as create_pool_postgresql
        await create_pool_postgresql(config)
    elif db_type == 'sqlite':
        from .sqlite import create_pool as create_pool_sqlite
        await create_pool_sqlite(config)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

@asynccontextmanager
async def get_db_connection():
    global pool
    db_type = config['database']['type']
    if db_type == 'postgresql':
        from .postgresql import get_db_connection as get_db_connection_postgresql
        async with get_db_connection_postgresql() as conn:
            yield conn
    elif db_type == 'sqlite':
        from .sqlite import get_db_connection as get_db_connection_sqlite
        async with get_db_connection_sqlite() as conn:
            yield conn
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

def init_db():
    db_type = config['database']['type']
    if db_type == 'postgresql':
        from .postgresql import init_db_postgresql
        return init_db_postgresql(config)
    elif db_type == 'sqlite':
        from .sqlite import init_db_sqlite
        return init_db_sqlite(config)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

def check_server_setup(server_id):
    db_type = config['database']['type']
    if db_type == 'postgresql':
        from .postgresql import check_server_setup_postgresql
        return check_server_setup_postgresql(server_id)
    elif db_type == 'sqlite':
        from .sqlite import check_server_setup_sqlite
        return check_server_setup_sqlite(server_id)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

def set_server_setup(server_id, debug_channel_id):
    db_type = config['database']['type']
    if db_type == 'postgresql':
        from .postgresql import set_server_setup_postgresql
        return set_server_setup_postgresql(server_id, debug_channel_id)
    elif db_type == 'sqlite':
        from .sqlite import set_server_setup_sqlite
        return set_server_setup_sqlite(server_id, debug_channel_id)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

def get_debug_channel(server_id):
    db_type = config['database']['type']
    if db_type == 'postgresql':
        from .postgresql import get_debug_channel_postgresql
        return get_debug_channel_postgresql(server_id)
    elif db_type == 'sqlite':
        from .sqlite import get_debug_channel_sqlite
        return get_debug_channel_sqlite(server_id)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

def set_welcome_channel(server_id, welcome_channel_id):
    db_type = config['database']['type']
    if db_type == 'postgresql':
        from .postgresql import set_welcome_channel_postgresql
        return set_welcome_channel_postgresql(server_id, welcome_channel_id)
    elif db_type == 'sqlite':
        from .sqlite import set_welcome_channel_sqlite
        return set_welcome_channel_sqlite(server_id, welcome_channel_id)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

def get_welcome_channel(server_id):
    db_type = config['database']['type']
    if db_type == 'postgresql':
        from .postgresql import get_welcome_channel_postgresql
        return get_welcome_channel_postgresql(server_id)
    elif db_type == 'sqlite':
        from .sqlite import get_welcome_channel_sqlite
        return get_welcome_channel_sqlite(server_id)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")