"""Module for working with positions"""
from datetime import date
from typing import List, Dict

from data import query
from common_utils import (
    get_all_by_table,
    get_current_date_string,
    clear_records_by_date,
    batch_insert,
    delete_old_records
)

class Position:
    """Position container class"""
    def __init__(self, title: str, count: int):
        self.count = count
        self.title = title

    @staticmethod
    def delete_positions_older_than_month() -> None:
        """Delete positions older than a month"""
        delete_old_records('positions_statistics')

    @staticmethod
    def save_positions(values: Dict[str, int]) -> None:
        """Save position statistics"""
        # Get position dictionary mapping names to IDs
        positions = get_all_by_table('positions')

        # Get current date
        date_collected = get_current_date_string()

        # Delete previous data for the current date
        clear_records_by_date('positions_statistics', date_collected)

        # Prepare batch insert data
        positions_list = []
        for position_name, count in values.items():
            # Get position id
            position_id = positions.get(position_name)
            if position_id is None:
                continue

            # Add to batch
            positions_list.append((position_id, count, date_collected))

        # Execute batch insert
        if positions_list:
            batch_insert(
                'positions_statistics',
                ['position_id', 'count', 'date_collected'],
                positions_list
            )

def get_positions() -> Dict[str, int]:
    """Get all positions with zero counts"""
    positions = get_all_by_table('positions')
    return {name: 0 for name in positions}

class PositionStatistic:
    """Position statistic container class"""
    def __init__(self, title: str, count: int):
        self.title = title
        self.count = count

def get_positions_statistics_by_date(date_collected: date) -> List[PositionStatistic]:
    """Get position statistics for a specific date"""
    positions_stat = []

    rows = query(
        "SELECT p.name, ps.count FROM positions_statistics AS ps "
        "JOIN positions AS p ON ps.position_id = p.id "
        "WHERE date_collected = %s ORDER BY ps.count DESC",
        parameters=[date_collected]
    )

    for row in rows:
        positions_stat.append(PositionStatistic(title=row[0], count=row[1]))

    return positions_stat