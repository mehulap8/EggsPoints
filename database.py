import os
import psycopg

def get_db_connection():
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    return psycopg.connect(database_url)

def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS egg_counts (
                name TEXT PRIMARY KEY,
                count INTEGER DEFAULT 0
            )
        ''')

def update_count(name, delta):
    with get_db_connection() as conn:
        conn.execute(
            'INSERT INTO egg_counts (name, count) VALUES (%s, %s) ON CONFLICT (name) DO UPDATE SET count = egg_counts.count + %s',
            (name.lower(), delta, delta)
        )

def get_all_counts():
    with get_db_connection() as conn:
        results = conn.execute('SELECT name, count FROM egg_counts ORDER BY count DESC').fetchall()
    return {name: count for name, count in results}

def reset_all():
    with get_db_connection() as conn:
        conn.execute('DELETE FROM egg_counts')

def bulk_insert_counts(counts_dict):
    with get_db_connection() as conn:
        conn.executemany(
            'INSERT INTO egg_counts (name, count) VALUES (%s, %s)',
            list(counts_dict.items())
        )
