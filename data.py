import os
import logging
import threading
from contextlib import contextmanager
from typing import List, Dict, Any, Optional

import mysql.connector
from mysql.connector import Error as MySQLError
from mysql.connector.connection import MySQLConnection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('database.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Global variables with thread-local storage
_thread_local = threading.local()

# Cached data management
_CACHED_DATA: Dict[str, Any] = {}


def get_cached_data() -> Dict[str, Any]:
    """
    Retrieve cached data.

    Returns:
        Dictionary of cached data
    """
    return _CACHED_DATA


def set_cached_data(input_data: Dict[str, Any]):
    """
    Set cached data.

    Args:
        input_data: Dictionary to cache
    """
    global _CACHED_DATA
    _CACHED_DATA = input_data


@contextmanager
def get_connection():
    """
    Context manager for database connections.

    Yields:
        MySQL database connection

    Raises:
        Exception: If connection fails
    """
    connection = None
    try:
        connection = mysql.connector.connect(
            user=os.environ['db_user'],
            password=os.environ['db_password'],
            host=os.environ['db_host'],
            database=os.environ['db_database'],
            charset='utf8mb4',
            connect_timeout=10,
            autocommit=True
        )

        # Set connection properties
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SET NAMES 'utf8mb4'")
            cursor.execute("SET CHARACTER SET 'utf8mb4'")
            cursor.execute("SET SESSION collation_connection = 'utf8mb4_unicode_ci'")
        finally:
            cursor.close()

        yield connection

    except mysql.connector.Error as err:
        logger.error(f"Database connection error: {err}")
        raise

    finally:
        if connection and connection.is_connected():
            connection.close()


def query(sql: str, **kwargs) -> List[Any]:
    """
    Execute a database query with robust error handling.

    Args:
        sql: SQL query to execute
        **kwargs: Additional parameters for query execution

    Returns:
        List of query results
    """
    parameters = kwargs.get('parameters', [])
    is_many = kwargs.get('many', False)
    max_retries = 3

    for attempt in range(max_retries):
        try:
            with get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                try:
                    # Execute the query
                    if is_many:
                        cursor.executemany(sql, parameters)
                    else:
                        cursor.execute(sql, parameters if parameters else None)

                    # Fetch results for SELECT queries
                    if sql.strip().upper().startswith('SELECT'):
                        results = cursor.fetchall()
                        return results

                    # Commit for non-SELECT queries
                    connection.commit()
                    return []

                finally:
                    cursor.close()

        except MySQLError as error:
            logger.error(f"Query attempt {attempt + 1} failed: {error}")
            logger.error(f"Query details: {sql}")

            # Log specific error details
            if error.errno == mysql.connector.errorcode.CR_SERVER_LOST:
                logger.warning("Lost connection to MySQL server. Retrying...")

            # Reraise on final attempt
            if attempt == max_retries - 1:
                logger.critical(f"Failed to execute query after {max_retries} attempts")
                raise

    return []


def close_connection():
    """
    Placeholder for connection closing (now handled by context manager).
    """
    logger.info("Connection management is now handled by context manager.")