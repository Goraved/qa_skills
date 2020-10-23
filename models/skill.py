import asyncio

from data import query


class Skill:
    def __init__(self):
        pass


async def get_skills():
    await asyncio.sleep(0)
    skills = {}
    cur = query("SELECT * FROM skills")
    for row in cur.fetchall():
        skills.update({row[1]: 0})
    return skills


async def get_skills_info():
    await asyncio.sleep(0)
    skills = []
    cur = query('SELECT id, name FROM skills ORDER BY name')
    for row in cur.fetchall():
        skills.append({'id': row[0], 'name': row[1]})
    return skills


def get_skill_list():
    skills = []
    cur = query('SELECT id, name FROM skills ORDER BY name')
    for row in cur.fetchall():
        skills.append({'id': row[0], 'name': row[1]})
    return skills
