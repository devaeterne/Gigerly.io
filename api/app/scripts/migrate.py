# api/app/scripts/migrate.py
"""Database migration utility script"""

import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from alembic.config import Config
from alembic import command
from app.config import settings
import logging

logger = logging.getLogger(__name__)

def run_migrations():
    """Run database migrations using Alembic"""
    try:
        # Set up Alembic configuration
        alembic_cfg = Config("alembic.ini")
        
        # Override the database URL from environment
        database_url = settings.DATABASE_URL.replace("+asyncpg", "+psycopg2")
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
        # Run migrations
        logger.info("Running database migrations...")
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrations completed successfully!")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

def create_migration(message: str):
    """Create a new migration"""
    try:
        alembic_cfg = Config("alembic.ini")
        database_url = settings.DATABASE_URL.replace("+asyncpg", "+psycopg2")
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
        logger.info(f"Creating migration: {message}")
        command.revision(alembic_cfg, message=message, autogenerate=True)
        logger.info("Migration created successfully!")
        
    except Exception as e:
        logger.error(f"Migration creation failed: {e}")
        raise

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "create":
        message = sys.argv[2] if len(sys.argv) > 2 else "Auto-generated migration"
        create_migration(message)
    else:
        run_migrations()