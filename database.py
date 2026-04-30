import os
import psycopg2
from psycopg2.extras import execute_values

def get_db_connection():
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    return psycopg2.connect(database_url)

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS egg_counts (
            name TEXT PRIMARY KEY,
            count INTEGER DEFAULT 0
        )
    ''')

    conn.commit()
    cur.close()
    conn.close()

def update_count(name, delta):
    """Update count for a person by delta (can be positive or negative)"""
    name_lower = name.lower()
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'INSERT INTO egg_counts (name, count) VALUES (%s, %s) ON CONFLICT (name) DO UPDATE SET count = egg_counts.count + %s',
        (name_lower, delta, delta)
    )

    conn.commit()
    cur.close()
    conn.close()

def get_all_counts():
    """Get all egg counts"""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT name, count FROM egg_counts ORDER BY count DESC')
    results = cur.fetchall()

    cur.close()
    conn.close()

    return {name: count for name, count in results}

def reset_all():
    """Clear all counts (used for backfill)"""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('DELETE FROM egg_counts')

    conn.commit()
    cur.close()
    conn.close()

def bulk_insert_counts(counts_dict):
    """Insert multiple counts at once"""
    conn = get_db_connection()
    cur = conn.cursor()

    data = [(name, count) for name, count in counts_dict.items()]

    execute_values(
        cur,
        'INSERT INTO egg_counts (name, count) VALUES %s',
        data
    )

    conn.commit()
    cur.close()
    conn.close()
