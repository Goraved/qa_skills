"""Module for working with statistics"""
from datetime import date
from typing import List, Dict, Any, Tuple

from data import query
from common_utils import (
    get_all_by_table,
    get_current_date_string,
    clear_records_by_date,
    batch_insert,
    delete_old_records,
    get_distinct_dates
)

class Statistic:
    """Statistic container class"""
    def __init__(self, percent: str, count: int, date_collected: str, **kwargs):
        self.skill_id = kwargs.get('skill_id')
        self.stat_id = kwargs.get('stat_id')
        self.title = kwargs.get('title')
        self.percent = percent
        self.count = count
        self.date_collected = date_collected

    @staticmethod
    def delete_stats_older_than_month() -> None:
        """Delete statistics older than a month"""
        delete_old_records('statistics')

    @staticmethod
    def get_str_dates() -> List[str]:
        """Get all distinct dates as strings"""
        return get_distinct_dates('statistics')

    @staticmethod
    def get_dates() -> List[date]:
        """Get all distinct dates as date objects"""
        return get_distinct_dates('statistics', as_string=False)

    @staticmethod
    def save_statistics(percent: Dict[str, str], count: Dict[str, int]) -> None:
        """Save statistics for skills"""
        # Get skill list
        skills = get_all_by_table('skills')

        # Get current date
        date_collected = get_current_date_string()

        # Delete previous data by current date
        clear_records_by_date('statistics', date_collected)

        # Prepare batch insert data
        stats_list = []
        for skill_name in percent:
            # Get skill id
            skill_id = skills.get(skill_name)
            if skill_id is None:
                continue

            # Add to the batch
            stats_list.append((skill_id, count[skill_name], percent.get(skill_name), date_collected))

        # Execute batch insert
        if stats_list:
            batch_insert(
                'statistics',
                ['skill_id', 'skill_count', 'skill_percent', 'date_collected'],
                stats_list
            )

def get_statistics_by_skill(skill_id: int) -> List[Statistic]:
    """Get statistics for a specific skill"""
    stats = []
    rows = query(
        "SELECT skill_id, skill_count, skill_percent, date_collected FROM statistics "
        "WHERE skill_id = %s ORDER BY date_collected DESC",
        parameters=[skill_id]
    )

    for row in rows:
        stats.append(Statistic(
            count=row[1],
            percent=row[2],
            date_collected=str(row[3]),
            skill_id=row[0]
        ))
    return stats

def get_statistics_by_date(date_collected: date) -> List[Statistic]:
    """Get statistics for a specific date"""
    stats = []
    rows = query(
        "SELECT sk.name, st.skill_percent, st.skill_count, st.date_collected, sk.id "
        "FROM statistics as st JOIN skills as sk ON st.skill_id = sk.id "
        "WHERE date_collected = %s ORDER BY st.skill_count DESC",
        parameters=[date_collected]
    )

    for row in rows:
        stats.append(Statistic(
            title=row[0],
            percent=row[1],
            count=row[2],
            date_collected=str(row[3]),
            stat_id=row[4]
        ))
    return stats