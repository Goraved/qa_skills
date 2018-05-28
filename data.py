import os
import time

import MySQLdb


def query(sql, **kwargs):
    db = MySQLdb.connect(user=os.environ['db_user'], password=os.environ['db_password'],
                         host=os.environ['db_host'], charset='utf8',
                         database=os.environ['db_database'], connect_timeout=600)
    try:
        cursor = db.cursor()
        cursor.execute("""SET NAMES 'utf8';
    SET CHARACTER SET 'utf8';
    SET SESSION collation_connection = 'utf8_general_ci';""")
    except:
        pass
    try:
        cursor = db.cursor()
        if kwargs.get('many', False):
            cursor.executemany(sql, kwargs.get('list', []))
        else:
            cursor.execute(sql)
    except (AttributeError, MySQLdb.OperationalError):
        db.ping(True)
        cursor = db.cursor()
        cursor.execute(sql)
    db.commit()
    db.close()
    return cursor


def get_skills():
    skills = {}
    cur = query("Select * from skills")
    for row in cur.fetchall():
        skills.update({row[1]: 0})
    cur.close()
    return skills


def get_positions():
    positions = {}
    cur = query("Select * from positions")
    for row in cur.fetchall():
        positions.update({row[1]: 0})
    cur.close()
    return positions


def get_ways():
    ways = {}
    cur = query("Select * from ways")
    for row in cur.fetchall():
        ways.update({row[1]: 0})
    cur.close()
    return ways


def get_english():
    english = {}
    cur = query("Select * from english")
    for row in cur.fetchall():
        english.update({row[1]: 0})
    cur.close()
    return english


def get_latest_statistics():
    stat = []
    cur = query("Select date_collected from statistics order by date_collected desc limit 1;")
    for row in cur.fetchall():
        latest = row[0]
    cur = query("""SELECT sk.name, st.skill_percent, st.skill_count, st.date_collected  FROM statistics as st 
JOIN skills as sk on st.skill_id = sk.id
where date_collected = '{}' order by st.skill_count DESC;""".format(latest))
    for row in cur.fetchall():
        stat.append({'title': row[0], 'percent': row[1], 'count': row[2], 'date': row[3]})
    return stat


def get_latest_ways_statistics():
    ways_stat = []
    cur = query("Select date_collected from ways_statistics order by date_collected desc limit 1;")
    for row in cur.fetchall():
        latest = row[0]
    cur = query("""SELECT w.name, ws.count  FROM ways_statistics as ws 
JOIN ways as w on ws.ways_id = w.id
where date_collected = '{}' order by ws.count DESC;""".format(latest))
    for row in cur.fetchall():
        ways_stat.append({'title': row[0], 'count': row[1]})
    return ways_stat


def get_latest_positions_statistics():
    positions_stat = []
    cur = query("Select date_collected from positions_statistics order by date_collected desc limit 1;")
    for row in cur.fetchall():
        latest = row[0]
    cur = query("""SELECT w.name, ps.count  FROM positions_statistics as ps 
JOIN positions as w on ps.position_id = w.id
where date_collected = '{}' order by ps.count DESC;""".format(latest))
    for row in cur.fetchall():
        positions_stat.append({'title': row[0], 'count': row[1]})
    return positions_stat


def get_latest_vacancies_statistics():
    vacancies_stat = []
    cur = query("Select date_collected from vacancies order by date_collected desc limit 1;")
    for row in cur.fetchall():
        latest = row[0]
    cur = query("SELECT *  FROM vacancies where date_collected = '{}';".format(latest))
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
    cur.close()


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
    cur.close()


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
    cur.close()


def save_vacancies(values):
    # Get vacancies list
    vacancies = {}
    # Get current date
    date = time.strftime('%Y-%m-%d')
    # Delete previous data by current date
    cur = query("Delete from vacancies where date_collected = '%s'" % date)
    list = []
    for result in values:
        # Save vacancies
        list.append((result['vacancy_title'], result['vacancy_link'], result['company_title'], result['company_link'],
                     result['city_title'], date))
    insert_query = "Insert into vacancies (vacancy, url, company, company_url, city, date_collected) values (%s, %s, %s, %s, %s, %s);"
    cur = query(insert_query, list=list, many=True)
    cur.close()
