#!/usr/bin/env python3
"""Reset the database with new schema"""
import os
import sys
sys.path.append('..')
from config import DATABASE_PATH
from database import Database

def reset_database():
    """Remove old database and create new one with updated schema"""

    # Remove existing database
    if os.path.exists(DATABASE_PATH):
        backup_name = DATABASE_PATH.replace('.db', '_backup.db')
        print(f"Backing up existing database to {backup_name}")
        os.rename(DATABASE_PATH, backup_name)

    # Create new database with updated schema
    print("Creating new database with VIN analysis schema...")
    db = Database()
    print(f"New database created at {DATABASE_PATH}")
    print("Ready for VIN-focused manual transmission hunting!")

if __name__ == "__main__":
    reset_database()
