import asyncio
import time
from datetime import date
from typing import List

from data import query


class Position:
    def __init__(self, title: str, count: int):
        self.count = count
        self.title = title

    @staticmethod
    async def delete_positions_older_than_month():
        await asyncio.sleep(0)
        query("DELETE FROM positions_statistics WHERE date_collected < NOW() - interval 31 DAY")

    @staticmethod
    def save_positions(values: dict):
        # Get position list
        positions = {}
        cur = query("SELECT * FROM positions")
        for row in cur.fetchall():
            positions.update({row[1]: row[0]})
        # Get current date
        date_collected = time.strftime('%Y-%m-%d')
        # Delete previous data by current date
        query(f"Delete FROM positions_statistics WHERE date_collected = '{date_collected}'")
        positions_list = []
        for result in values:
            # Get position id
            position_id = positions.get(result)
            # Save statistic by position
            positions_list.append((position_id, values.get(result), date_collected))
        insert_query = "Insert into positions_statistics (position_id, count, date_collected) values (%s, %s, %s);"
        query(insert_query, parameters=positions_list, many=True)


async def get_positions() -> dict:
    await asyncio.sleep(0)
    positions = {}
    cur = query("SELECT * FROM positions")
    for row in cur.fetchall():
        positions.update({row[1]: 0})
    return positions


class PositionStatistic:
    def __init__(self, title: str, count: int):
        self.title = title
        self.count = count


async def get_positions_statistics_by_date(date_collected: date) -> List[PositionStatistic]:
    await asyncio.sleep(0)
    positions_stat = []
    cur = query(f"SELECT w.name, ps.count  FROM positions_statistics as ps "
                f"JOIN positions as w on ps.position_id = w.id WHERE date_collected = '{date_collected}' "
                f"ORDER BY ps.count DESC;")
    for row in cur.fetchall():
        positions_stat.append(PositionStatistic(title=row[0], count=row[1]))
    return positions_stat
