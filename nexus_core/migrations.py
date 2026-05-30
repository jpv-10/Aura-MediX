"""
AURA MEDIX — Database Migrations
Handle schema changes and column additions safely
"""

import logging
from sqlalchemy import inspect, text

logger = logging.getLogger(__name__)


def add_column_if_not_exists(db, table_name, column_name, column_type):
    """
    Safely add a column to a table if it doesn't already exist.
    Works with SQLite, PostgreSQL, and MySQL.
    """
    try:
        inspector = inspect(db.engine)
        
        # Check if table exists
        if table_name not in inspector.get_table_names():
            logger.warning(f"[Migration] Table {table_name} does not exist")
            return False
        
        # Get existing columns
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        
        # Check if column already exists
        if column_name in columns:
            logger.info(f"[Migration] Column {table_name}.{column_name} already exists")
            return True
        
        # Determine database type
        dialect_name = db.engine.dialect.name
        
        # Add column based on database type
        if dialect_name == 'sqlite':
            # SQLite ALTER TABLE syntax
            alter_sql = f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}'
        elif dialect_name == 'postgresql':
            # PostgreSQL ALTER TABLE syntax
            alter_sql = f'ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_name} {column_type}'
        elif dialect_name == 'mysql':
            # MySQL ALTER TABLE syntax
            alter_sql = f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}'
        else:
            logger.error(f"[Migration] Unsupported database dialect: {dialect_name}")
            return False
        
        # Execute the ALTER TABLE statement
        with db.engine.connect() as connection:
            connection.execute(text(alter_sql))
            connection.commit()
        
        logger.info(f"[Migration] Column {table_name}.{column_name} added successfully")
        return True
        
    except Exception as e:
        logger.error(f"[Migration] Error adding column {table_name}.{column_name}: {e}")
        return False


def drop_column_if_exists(db, table_name, column_name):
    """
    Safely drop a column from a table if it exists.
    Note: Some databases have restrictions on dropping columns.
    """
    try:
        inspector = inspect(db.engine)
        
        # Check if table exists
        if table_name not in inspector.get_table_names():
            logger.warning(f"[Migration] Table {table_name} does not exist")
            return False
        
        # Get existing columns
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        
        # Check if column exists
        if column_name not in columns:
            logger.info(f"[Migration] Column {table_name}.{column_name} does not exist")
            return True
        
        # Determine database type
        dialect_name = db.engine.dialect.name
        
        # Drop column based on database type
        if dialect_name == 'sqlite':
            # SQLite doesn't support direct DROP COLUMN (requires complex migration)
            logger.warning(f"[Migration] SQLite does not support direct DROP COLUMN")
            return False
        elif dialect_name == 'postgresql':
            # PostgreSQL ALTER TABLE syntax
            alter_sql = f'ALTER TABLE {table_name} DROP COLUMN IF EXISTS {column_name}'
        elif dialect_name == 'mysql':
            # MySQL ALTER TABLE syntax
            alter_sql = f'ALTER TABLE {table_name} DROP COLUMN {column_name}'
        else:
            logger.error(f"[Migration] Unsupported database dialect: {dialect_name}")
            return False
        
        # Execute the ALTER TABLE statement
        with db.engine.connect() as connection:
            connection.execute(text(alter_sql))
            connection.commit()
        
        logger.info(f"[Migration] Column {table_name}.{column_name} dropped successfully")
        return True
        
    except Exception as e:
        logger.error(f"[Migration] Error dropping column {table_name}.{column_name}: {e}")
        return False


def run_migrations(db):
    """
    Run all pending database migrations.
    This is called during app initialization.
    """
    logger.info("[Migration] Starting database migrations...")
    
    try:
        # Migrate reports table
        logger.info("[Migration] Migrating reports table...")
        add_column_if_not_exists(db, 'reports', 'disease_name', 'VARCHAR(100)')
        add_column_if_not_exists(db, 'reports', 'prediction_id', 'INTEGER')
        
        # Migrate vital_signs table
        logger.info("[Migration] Migrating vital_signs table...")
        add_column_if_not_exists(db, 'vital_signs', 'respiratory_rate', 'FLOAT')
        
        # Migrate health_timeline table
        logger.info("[Migration] Migrating health_timeline table...")
        add_column_if_not_exists(db, 'health_timeline', 'prediction_id', 'INTEGER')
        add_column_if_not_exists(db, 'health_timeline', 'event_type', 'VARCHAR(50)')
        add_column_if_not_exists(db, 'health_timeline', 'disease_analyzed', 'VARCHAR(100)')
        add_column_if_not_exists(db, 'health_timeline', 'result', 'VARCHAR(100)')
        add_column_if_not_exists(db, 'health_timeline', 'ai_recommendation', 'TEXT')
        add_column_if_not_exists(db, 'health_timeline', 'data', 'TEXT')
        
        # Migrate disease_predictions table
        logger.info("[Migration] Migrating disease_predictions table...")
        add_column_if_not_exists(db, 'disease_predictions', 'input_data', 'TEXT')
        add_column_if_not_exists(db, 'disease_predictions', 'model_used', 'VARCHAR(50)')
        
        logger.info("[Migration] Database migrations completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"[Migration] Error during migrations: {e}")
        return False
