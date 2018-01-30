import time

import MySQLdb


def query(sql):
    db = MySQLdb.connect(user='qaskills', password='Cf4V~g336_8Z',
                         host='den1.mysql5.gear.host',
                         database='qaskills', connect_timeout=600)
    try:
        cursor = db.cursor()
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


def save_statistics(results):
    # Get skill list
    skills = {}
    cur = query("Select * from skills")
    for row in cur.fetchall():
        skills.update({row[1]: row[0]})
    # Get current date
    date = time.strftime('%Y-%m-%d')
    # Delete previous data by current date
    cur = query("Delete from statistics where date_collected = '%s'" % date)
    for result in results:
        # Get skill id
        skill_id = skills.get(result)
        # Save statistic by skill
        insert_query = "Insert into statistics (skill_id, skill_percent, date_collected) values (%s,'%s','%s');" % (
            skill_id, results.get(result), date)
        cur = query(insert_query)
    cur.close()
#
#
#
# def close_db():
#     db.close()
