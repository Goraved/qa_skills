"""Module for working with ways"""
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

class Way:
    """Way container class"""
    def __init__(self, title: str, count: int):
        self.count = count
        self.title = title

    @staticmethod
    def delete_ways_older_than_month() -> None:
        """Delete ways older than a month"""
        delete_old_records('ways_statistics')

    @staticmethod
    def save_ways(values: Dict[str, int]) -> None:
        """Save way statistics"""
        # Get way dictionary mapping names to IDs
        ways = get_all_by_table('ways')

        # Get current date
        date_collected = get_current_date_string()

        # Delete previous data for current date
        clear_records_by_date('ways_statistics', date_collected)

        # Prepare batch insert data
        ways_list = []
        for way_name, count in values.items():
            # Get way id
            way_id = ways.get(way_name)
            if way_id is None:
                continue

            # Add to batch
            ways_list.append((way_id, count, date_collected))

        # Execute batch insert
        if ways_list:
            batch_insert(
                'ways_statistics',
                ['ways_id', 'count', 'date_collected'],
                ways_list
            )

def get_ways() -> Dict[str, int]:
    """Get all ways with zero counts"""
    ways = get_all_by_table('ways')
    return {name: 0 for name in ways}

class WayStatistic:
    """Way statistic container class"""
    def __init__(self, title: str, count: int):
        self.title = title
        self.count = count

def get_ways_statistics_by_date(date_collected: date) -> List[WayStatistic]:
    """Get way statistics for a specific date"""
    ways_stat = []

    rows = query(
        "SELECT w.name, ws.count FROM ways_statistics AS ws "
        "JOIN ways AS w ON ws.ways_id = w.id "
        "WHERE date_collected = %s ORDER BY ws.count DESC",
        parameters=[date_collected]
    )

    for row in rows:
        ways_stat.append(WayStatistic(title=row[0], count=row[1]))

    return ways_stat