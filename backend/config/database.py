"""Database configuration and connection utilities"""

import pymysql
import logging
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from .settings import settings

logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration settings"""
    HOST = settings.db_host
    PORT = settings.db_port
    USER = settings.db_user
    PASSWORD = settings.db_password
    DATABASE = settings.db_name
    CHARSET = settings.db_charset

def get_connection():
    """Get database connection with improved error handling"""
    try:
        return pymysql.connect(
            host=DatabaseConfig.HOST,
            port=DatabaseConfig.PORT,
            user=DatabaseConfig.USER,
            password=DatabaseConfig.PASSWORD,
            database=DatabaseConfig.DATABASE,
            charset=DatabaseConfig.CHARSET,
            connect_timeout=10,
            autocommit=True
        )
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    connection = None
    try:
        connection = get_connection()
        yield connection
    except Exception as e:
        logger.error(f"Database operation failed: {str(e)}")
        if connection:
            connection.rollback()
        raise
    finally:
        if connection:
            connection.close()

def execute_query(query: str, params: Optional[List] = None) -> List[tuple]:
    """Execute a query and return results"""
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params or [])
            return cursor.fetchall()

def execute_query_one(query: str, params: Optional[List] = None) -> Optional[tuple]:
    """Execute a query and return single result"""
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params or [])
            return cursor.fetchone()

def execute_query_dict(query: str, params: Optional[List] = None) -> List[Dict[str, Any]]:
    """Execute a query and return results as list of dictionaries"""
    with get_db_connection() as connection:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query, params or [])
            return cursor.fetchall()

def execute_insert(query: str, params: Optional[List] = None) -> int:
    """Execute an insert query and return the last insert ID"""
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params or [])
            return cursor.lastrowid

def execute_update(query: str, params: Optional[List] = None) -> int:
    """Execute an update/delete query and return affected rows"""
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params or [])
            return cursor.rowcount
