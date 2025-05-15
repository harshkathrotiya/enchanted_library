import os

DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://postgres:postgres@localhost:5432/enchanted_library_new'
)

# Default database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'enchanted_library_new',
    'user': 'postgres',
    'password': 'postgres'
}