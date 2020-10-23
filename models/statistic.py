import asyncio
import time
from datetime import date
from typing import List

from data import query


class Statistic:
    def __init__(self, percent: str, count: int, date_collected: str, **kwargs):
        self.skill_id = kwargs.get('skill_id')
        self.stat_id = kwargs.get('stat_id')
        self.title = kwargs.get('title')
        self.percent = percent
        self.count = count
        self.date_collected = date_collected

    @staticmethod
    async def delete_stats_older_than_month():
        await asyncio.sleep(0)
        query("DELETE FROM statistics WHERE date_collected < NOW() - interval 31 DAY")

    @staticmethod
    def get_str_dates() -> List[str]:
        dates = []
        cur = query("SELECT distinct date_collected FROM statistics ORDER BY id DESC")
        for row in cur.fetchall():
            dates.append(str(row[0]))
        return dates

    @staticmethod
    def get_dates() -> List[date]:
        dates = []
        cur = query("SELECT distinct date_collected FROM statistics ORDER BY id DESC")
        for row in cur.fetchall():
            dates.append(row[0])
        return dates

    @staticmethod
    def save_statistics(percent: dict, count: dict):
        # Get skill list
        skills = {}
        cur = query("SELECT * FROM skills")
        for row in cur.fetchall():
            skills.update({row[1]: row[0]})
        # Get current date
        date_collected = time.strftime('%Y-%m-%d')
        # Delete previous data by current date
        query(f"Delete FROM statistics WHERE date_collected = '{date_collected}'")
        stats_list = []
        for result in percent:
            # Get skill id
            skill_id = skills.get(result)
            # Save statistic by skill
            stats_list.append((skill_id, count[result], percent.get(result), date_collected))
        insert_query = "Insert into statistics (skill_id, skill_count, skill_percent, date_collected) " \
                       "values (%s, %s, %s, %s);"
        query(insert_query, parameters=stats_list, many=True)


async def get_statistics_by_skill(skill_id: int) -> List[Statistic]:
    await asyncio.sleep(0)
    stats = []
    cur = query(f"SELECT skill_id, skill_count, skill_percent, date_collected from statistics "
                f"WHERE skill_id = {skill_id} ORDER BY date_collected DESC")
    for row in cur.fetchall():
        stats.append(Statistic(count=row[1], percent=row[2], date_collected=str(row[3]), skill_id=row[0]))
    return stats


async def get_statistics_by_date(date_collected: date) -> List[Statistic]:
    await asyncio.sleep(0)
    stat = []
    cur = query(
        f"SELECT sk.name, st.skill_percent, st.skill_count, st.date_collected, sk.id  FROM statistics as st "
        f"JOIN skills as sk on st.skill_id = sk.id WHERE date_collected = '{date_collected}'"
        f" ORDER BY st.skill_count DESC;")
    for row in cur.fetchall():
        stat.append(Statistic(title=row[0], percent=row[1], count=row[2], date_collected=str(row[3]), stat_id=row[4]))
    return stat
