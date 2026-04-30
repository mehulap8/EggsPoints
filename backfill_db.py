#!/usr/bin/env python3
"""
Backfill database with egg counts from message history.
Run this once after deploying the database setup.

Usage: python backfill_db.py
"""

import os
from count_eggs import calculate_egg_counts, load_name_mappings
from database import init_db, reset_all, bulk_insert_counts

GROUP_ID = 27967386

def backfill():
    print("Initializing database...")
    init_db()

    print("Clearing existing counts...")
    reset_all()

    print("Fetching all messages and calculating counts...")
    result = calculate_egg_counts(GROUP_ID)

    egg_counts = result['egg_counts']
    primary_to_display = result['primary_to_display']

    print(f"Found {len(egg_counts)} people with egg counts")

    print("Inserting into database...")
    bulk_insert_counts(egg_counts)

    print("\nBackfill complete! Counts:")
    sorted_eggs = sorted(egg_counts.items(), key=lambda x: x[1], reverse=True)
    for name, count in sorted_eggs:
        display_name = primary_to_display.get(name, name)
        eggs = '🥚' * (count // 50)
        print(f"{display_name}:{eggs} {count}")

if __name__ == '__main__':
    backfill()
