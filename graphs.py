import asyncio
import os
from datetime import date
from typing import List, Tuple

import matplotlib
import matplotlib.pyplot as plt
from flask import abort

from models.position import get_positions_statistics_by_date
from models.skill import get_skills_info
from models.statistic import get_statistics_by_skill, get_statistics_by_date, Statistic
from models.vacancy import get_vacancies_statistics_by_date
from models.way import get_ways_statistics_by_date

PLT = plt


def get_stats(date_collected: date) -> Tuple:
    if not os.path.isfile('./static/images/languages.png'):
        get_languages_comparison()
    iloop = asyncio.new_event_loop()
    asyncio.set_event_loop(iloop)
    tasks = [get_vacancies_statistics_by_date(date_collected), get_positions_statistics_by_date(date_collected),
             get_ways_statistics_by_date(date_collected), get_statistics_by_date(date_collected)]
    a_results = iloop.run_until_complete(asyncio.gather(*tasks))
    links = a_results[0]
    positions = a_results[1]
    ways = a_results[2]
    stats = a_results[3]
    tech = [{'vac_count': len(links), 'date_collected': stats[0].date_collected}]
    return links, stats, positions, ways, tech


def get_skill_stats(skill_id: int) -> Tuple:
    iloop = asyncio.new_event_loop()
    asyncio.set_event_loop(iloop)
    tasks = [get_statistics_by_skill(skill_id), get_skills_info()]
    result = iloop.run_until_complete(asyncio.gather(*tasks))
    stats = result[0]
    skills = result[1]
    selected_skill = [_ for _ in skills if _['id'] == skill_id]
    if not selected_skill:
        abort(400, f'Unknown skill_id - "{skill_id}"')
    save_graph(stats, selected_skill[0]["name"])
    return stats, skills, selected_skill


def save_graph(stats: List[Statistic], name: str, title='graph'):
    matplotlib.use('agg')
    if not PLT.axes().legend_ or name not in [element._text for element in PLT.axes().legend_.texts]:
        count_skill = [stat.count for stat in stats][::-1]
        date_collected = [stat.date_collected for stat in stats][::-1]
        PLT.plot(date_collected, count_skill, label=name)
        PLT.title = title
        PLT.legend(loc="upper left")
        PLT.ylabel('Skill matched in vacancies')
        PLT.xlabel('Date collected')
        PLT.xticks(rotation=90)
        PLT.savefig(f'static/images/{title}.png')


def get_languages_comparison():
    for skill_id in (6, 7, 10, 11, 46):
        iloop_lang = asyncio.new_event_loop()
        asyncio.set_event_loop(iloop_lang)
        tasks = [get_statistics_by_skill(skill_id), get_skills_info()]
        result = iloop_lang.run_until_complete(asyncio.gather(*tasks))
        stats = result[0]
        skills = result[1]
        selected_skill = [_ for _ in skills if _['id'] == skill_id]
        save_graph(stats, selected_skill[0]["name"], 'languages')
        iloop_lang.close()
    clear_plt()
    from PIL import Image
    img = Image.open('static/images/languages.png')
    width, height = img.size
    img.crop((0, 50, width, height)).save('static/images/languages.png')


def clear_plt():
    PLT.close()
