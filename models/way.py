import asyncio
import time
from datetime import date
from typing import List

from data import query


class Way:
    def __init__(self, title: str, count: int):
        self.count = count
        self.title = title

    @staticmethod
    async def delete_ways_older_than_month():
        await asyncio.sleep(0)
        query("DELETE FROM ways_statistics WHERE date_collected < NOW() - interval 31 DAY")

    @staticmethod
    def save_ways(values: dict):
        # Get way list
        ways = {}
        cur = query("SELECT * FROM ways")
        for row in cur.fetchall():
            ways.update({row[1]: row[0]})
        # Get current date
        date_collected = time.strftime('%Y-%m-%d')
        # Delete previous data by current date
        query(f"Delete FROM ways_statistics WHERE date_collected = '{date_collected}'")
        ways_list = []
        for result in values:
            # Get way id
            way_id = ways.get(result)
            # Save statistic by way
            ways_list.append((way_id, values.get(result), date_collected))
        insert_query = "Insert into ways_statistics (ways_id, count, date_collected) values (%s, %s, %s);"
        query(insert_query, parameters=ways_list, many=True)


async def get_ways() -> dict:
    await asyncio.sleep(0)
    ways = {}
    cur = query("SELECT * FROM ways")
    for row in cur.fetchall():
        ways.update({row[1]: 0})
    return ways


class WayStatistic:
    def __init__(self, title: str, count: int):
        self.title = title
        self.count = count


async def get_ways_statistics_by_date(date_collected: date) -> List[WayStatistic]:
    await asyncio.sleep(0)
    ways_stat = []
    cur = query(f"SELECT w.name, ws.count  FROM ways_statistics as ws JOIN ways as w on ws.ways_id = w.id "
                f"WHERE date_collected = '{date_collected}' ORDER BY ws.count DESC;")
    for row in cur.fetchall():
        ways_stat.append(WayStatistic(title=row[0], count=row[1]))
    return ways_stat
