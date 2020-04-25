import asyncio
import os
import time
from datetime import datetime

import MySQLdb
import matplotlib
import matplotlib.pyplot as plt

DB = None


def db_connection():
    global DB
    DB = MySQLdb.connect(user=os.environ['db_user'], password=os.environ['db_password'],
                         host=os.environ['db_host'], charset='utf8',
                         database=os.environ['db_database'], connect_timeout=600)
    DB.ping(True)
    try:
        cursor = DB.cursor()
        cursor.execute("""SET NAMES 'utf8';
               SET CHARACTER SET 'utf8';
               SET SESSION collation_connection = 'utf8_general_ci';""")
    except:
        pass


def close_connection():
    global DB
    if DB:
        DB.close()


def query(sql, **kwargs):
    if not DB:
        db_connection()

    try:
        cursor = DB.cursor()
        if kwargs.get('many', False):
            cursor.executemany(sql, kwargs.get('list', []))
            DB.commit()
        else:
            cursor.execute(sql)
            DB.commit()
    except:
        db_connection()
        cursor = DB.cursor()
        cursor.execute(sql)
        DB.commit()
    return cursor


async def get_skills():
    await asyncio.sleep(0)
    skills = {}
    cur = query("Select * from skills")
    for row in cur.fetchall():
        skills.update({row[1]: 0})
    return skills


async def delete_stats_older_than_month():
    await asyncio.sleep(0)
    query("DELETE FROM statistics WHERE date_collected < NOW() - interval 31 DAY")


async def delete_vacancies_older_than_month():
    await asyncio.sleep(0)
    query("DELETE FROM vacancies WHERE date_collected < NOW() - interval 31 DAY")


async def delete_ways_older_than_month():
    await asyncio.sleep(0)
    query("DELETE FROM ways_statistics WHERE date_collected < NOW() - interval 31 DAY")


async def delete_positions_older_than_month():
    await asyncio.sleep(0)
    query("DELETE FROM positions_statistics WHERE date_collected < NOW() - interval 31 DAY")


def get_task_state(task_key):
    tasks = []
    cur = query(f"Select task_state from tasks where task_key like '{task_key}';")
    for row in cur.fetchall():
        tasks.append(row[0])
    return tasks[0]


def create_task(task_key):
    cur_date = datetime.now()
    query(f"Insert into tasks (task_key, task_state, date_created) values ({task_key}, 'False', '{cur_date}');")


async def complete_task(task_key):
    await asyncio.sleep(0)
    cur_date = datetime.now()
    query(f"Update tasks set task_state='True', date_finished='{cur_date}' where task_key like '{task_key}';")


async def get_positions():
    await asyncio.sleep(0)
    positions = {}
    cur = query("Select * from positions")
    for row in cur.fetchall():
        positions.update({row[1]: 0})
    return positions


async def get_ways():
    await asyncio.sleep(0)
    ways = {}
    cur = query("Select * from ways")
    for row in cur.fetchall():
        ways.update({row[1]: 0})
    return ways


def get_english():
    english = {}
    cur = query("Select * from english")
    for row in cur.fetchall():
        english.update({row[1]: 0})
    return english


def get_dates():
    dates = []
    cur = query(f"Select distinct date_collected from statistics order by id desc")
    for row in cur.fetchall():
        dates.append(str(row[0]))
    return dates


async def get_statistics_by_date(date_collected):
    await asyncio.sleep(0)
    stat = []
    # cur = query("Select date_collected from statistics order by date_collected desc limit 1;")
    # for row in cur.fetchall():
    #     latest = row[0]
    cur = query("""SELECT sk.name, st.skill_percent, st.skill_count, st.date_collected, sk.id  FROM statistics as st 
JOIN skills as sk on st.skill_id = sk.id
where date_collected = '{}' order by st.skill_count DESC;""".format(date_collected))
    for row in cur.fetchall():
        stat.append({'title': row[0], 'percent': row[1], 'count': row[2], 'date': str(row[3]), 'id': row[4]})
    return stat


async def get_ways_statistics_by_date(date_collected):
    await asyncio.sleep(0)
    ways_stat = []
    # cur = query("Select date_collected from ways_statistics order by date_collected desc limit 1;")
    # for row in cur.fetchall():
    #     latest = row[0]
    cur = query("""SELECT w.name, ws.count  FROM ways_statistics as ws 
JOIN ways as w on ws.ways_id = w.id
where date_collected = '{}' order by ws.count DESC;""".format(date_collected))
    for row in cur.fetchall():
        ways_stat.append({'title': row[0], 'count': row[1]})
    return ways_stat


async def get_positions_statistics_by_date(date_collected):
    await asyncio.sleep(0)
    positions_stat = []
    # cur = query("Select date_collected from positions_statistics order by date_collected desc limit 1;")
    # for row in cur.fetchall():
    #     latest = row[0]
    cur = query("""SELECT w.name, ps.count  FROM positions_statistics as ps 
JOIN positions as w on ps.position_id = w.id
where date_collected = '{}' order by ps.count DESC;""".format(date_collected))
    for row in cur.fetchall():
        positions_stat.append({'title': row[0], 'count': row[1]})
    return positions_stat


async def get_vacancies_statistics_by_date(date_collected):
    await asyncio.sleep(0)
    vacancies_stat = []
    # cur = query("Select date_collected from vacancies order by date_collected desc limit 1;")
    # for row in cur.fetchall():
    #     latest = row[0]
    cur = query("SELECT *  FROM vacancies where date_collected = '{}';".format(date_collected))
    for row in cur.fetchall():
        vacancies_stat.append(
            {'vacancy_title': row[1], 'vacancy_link': row[4], 'company_title': row[2], 'company_link': row[6],
             'city_title': row[3]})
    return vacancies_stat


def save_statistics(percent, count):
    # Get skill list
    skills = {}
    cur = query("Select * from skills")
    for row in cur.fetchall():
        skills.update({row[1]: row[0]})
    # Get current date
    date = time.strftime('%Y-%m-%d')
    # Delete previous data by current date
    cur = query("Delete from statistics where date_collected = '%s'" % date)
    list = []
    for result in percent:
        # Get skill id
        skill_id = skills.get(result)
        # Save statistic by skill
        list.append((skill_id, count[result], percent.get(result), date))
    insert_query = "Insert into statistics (skill_id, skill_count, skill_percent, date_collected) values (%s, %s, %s, %s);"
    cur = query(insert_query, list=list, many=True)


def save_positions(values):
    # Get position list
    positions = {}
    cur = query("Select * from positions")
    for row in cur.fetchall():
        positions.update({row[1]: row[0]})
    # Get current date
    date = time.strftime('%Y-%m-%d')
    # Delete previous data by current date
    cur = query("Delete from positions_statistics where date_collected = '%s'" % date)
    list = []
    for result in values:
        # Get position id
        position_id = positions.get(result)
        # Save statistic by position
        list.append((position_id, values.get(result), date))
    insert_query = "Insert into positions_statistics (position_id, count, date_collected) values (%s, %s, %s);"
    cur = query(insert_query, list=list, many=True)


def save_ways(values):
    # Get way list
    ways = {}
    cur = query("Select * from ways")
    for row in cur.fetchall():
        ways.update({row[1]: row[0]})
    # Get current date
    date = time.strftime('%Y-%m-%d')
    # Delete previous data by current date
    cur = query("Delete from ways_statistics where date_collected = '%s'" % date)
    list = []
    for result in values:
        # Get way id
        way_id = ways.get(result)
        # Save statistic by way
        list.append((way_id, values.get(result), date))
    insert_query = "Insert into ways_statistics (ways_id, count, date_collected) values (%s, %s, %s);"
    cur = query(insert_query, list=list, many=True)


def save_vacancies(values, vac_skills):
    # Get vacancies list
    vacancies = {}
    # Get current date
    date = time.strftime('%Y-%m-%d')
    # Delete previous data by current date
    cur = query("Delete from vacancies where date_collected = '%s'" % date)
    vac_list = []
    for result in values:
        # Save vacancies
        if not result:
            continue
        skills = [_['skills'] for _ in vac_skills if _['link'] in result['vacancy_link']][0]
        vac_list.append(
            (result['vacancy_title'], result['vacancy_link'], result['company_title'], result['company_link'],
             result['city_title'], date, skills))
    insert_query = "Insert into vacancies (vacancy, url, company, company_url, city, date_collected, skills) values (%s, %s, %s, %s, %s, %s, %s);"
    cur = query(insert_query, list=vac_list, many=True)


async def get_statistics_by_skill(skill_id):
    await asyncio.sleep(0)
    stats = []
    cur = query(
        f"""select skill_id, skill_count, skill_percent, date_collected from statistics where skill_id = {skill_id} 
        order by date_collected desc""")
    for row in cur.fetchall():
        stats.append(
            {'skill_id': row[0], 'skill_count': row[1], 'skill_percent': row[2], 'date_collected': str(row[3])})
    return stats


async def get_skills_info():
    await asyncio.sleep(0)
    skills = []
    cur = query(f'select id, name from skills order by name')
    for row in cur.fetchall():
        skills.append({'id': row[0], 'name': row[1]})
    return skills


def get_stats(date):
    if not os.path.isfile('./static/images/languages.png'):
        get_languages_comparison()
    iloop = asyncio.new_event_loop()
    asyncio.set_event_loop(iloop)
    tasks = [get_vacancies_statistics_by_date(date), get_positions_statistics_by_date(date),
             get_ways_statistics_by_date(date), get_statistics_by_date(date)]
    a_results = iloop.run_until_complete(asyncio.gather(*tasks))
    links = a_results[0]
    positions = a_results[1]
    ways = a_results[2]
    stats = a_results[3]
    tech = [{'vac_count': len(links), 'date_collected': stats[0]['date']}]
    return links, stats, positions, ways, tech


def get_skill_stats(skill_id):
    iloop = asyncio.new_event_loop()
    asyncio.set_event_loop(iloop)
    tasks = [get_statistics_by_skill(skill_id), get_skills_info()]
    result = iloop.run_until_complete(asyncio.gather(*tasks))
    stats = result[0]
    skills = result[1]
    selected_skill = [_ for _ in skills if str(_['id']) == skill_id]
    save_graph(stats, selected_skill[0]["name"])
    return stats, skills, selected_skill


PLT = plt


def save_graph(stats, name, title='graph'):
    matplotlib.use('agg')
    if not PLT.axes().legend_ or name not in [_._text for _ in PLT.axes().legend_.texts]:
        count_skill = [_['skill_count'] for _ in stats][::-1]
        date_collected = [_['date_collected'] for _ in stats][::-1]
        PLT.plot(date_collected, count_skill, label=name)
        PLT.title = title
        PLT.legend(loc="upper right")
        PLT.ylabel(f'Skill matched in vacancies')
        PLT.xlabel(f'Date collected')
        PLT.xticks(rotation=90)
        PLT.savefig(f'static/images/{title}.png')


def get_languages_comparison():
    for skill_id in (6, 7, 9, 10, 11, 19, 46, 94):
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
    w, h = img.size
    img.crop((0, 50, w, h)).save('static/images/languages.png')


def clear_plt():
    PLT.close()


def get_vacancies_by_skill(date_collected, skill):
    v = {'skill': skill}
    vacancies = []
    cur = query(
        f"SELECT distinct vacancy, url, company, city FROM vacancies where date_collected = '{date_collected}' "
        f"and (skills like '%|{skill}|%' OR skills like '{skill}|%' OR skills like '%|{skill}' OR skills like '{skill}')")
    for row in cur.fetchall():
        vacancies.append({'vacancy': row[0], 'url': row[1], 'company': row[2], 'city': row[3]})
    v['vacancies'] = vacancies
    return v


def get_skill_list():
    skills = []
    cur = query('select id, name from skills order by name')
    for row in cur.fetchall():
        skills.append({'id': row[0], 'name': row[1]})
    return skills
