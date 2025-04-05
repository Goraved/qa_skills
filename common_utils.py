"""Common utility functions for database operations"""
import logging
from datetime import date
from typing import List, Dict, Any, Tuple, Optional

from data import query

logger = logging.getLogger(__name__)

def get_current_date_string() -> str:
    """Return current date in YYYY-MM-DD format"""
    from time import strftime
    return strftime('%Y-%m-%d')

def get_all_by_table(table_name: str, id_column: str = 'id', name_column: str = 'name') -> Dict[str, int]:
    """Generic function to get all records from a table and return as dict {name: id}"""
    result = {}
    rows = query(f"SELECT {id_column}, {name_column} FROM {table_name}")
    for row in rows:
        result[row[1]] = row[0]
    return result

def delete_old_records(table_name: str, date_column: str = 'date_collected', days: int = 31) -> None:
    """Generic function to delete records older than specified days"""
    query(f"DELETE FROM {table_name} WHERE {date_column} < NOW() - interval {days} DAY")

def clear_records_by_date(table_name: str, date_value: str, date_column: str = 'date_collected') -> None:
    """Generic function to delete records for a specific date"""
    query(f"DELETE FROM {table_name} WHERE {date_column} = '{date_value}'")

def batch_insert(table_name: str, columns: List[str], values: List[Tuple], delimiter: str = ',') -> None:
    """Generic function for batch insert"""
    if not values:
        logger.warning(f"No values to insert into {table_name}")
        return

    placeholders = ', '.join(['%s'] * len(columns))
    columns_str = delimiter.join(columns)
    insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"

    query(insert_query, parameters=values, many=True)

def get_distinct_dates(table_name: str, date_column: str = 'date_collected',
                       as_string: bool = True) -> List[Any]:
    """Generic function to get distinct dates from a table"""
    rows = query(f"SELECT DISTINCT {date_column} FROM {table_name} ORDER BY {date_column} DESC")

    if as_string:
        return [str(row[0]) for row in rows]
    return [row[0] for row in rows]