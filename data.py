import os

import MySQLdb
from MySQLdb.cursors import Cursor


DB = None
CACHED_DATA = None


def get_cached_data() -> dict:
    return CACHED_DATA


def set_cached_data(input_data: dict):
    global CACHED_DATA
    CACHED_DATA = input_data


def db_connection():
    global DB
    DB = MySQLdb.connect(user=os.environ['db_user'], password=os.environ['db_password'],
                         host=os.environ['db_host'], charset='utf8',
                         database=os.environ['db_database'], connect_timeout=6000)
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


def query(sql: str, **kwargs) -> Cursor:
    if not DB:
        db_connection()

    for _ in range(10):
        try:
            cursor = DB.cursor()
            if kwargs.get('many', False):
                cursor.executemany(sql, kwargs.get('parameters', []))
            else:
                cursor.execute(sql)
            DB.commit()
            break
        except Exception as e:
            print(f'SQL Error - {e} for query - {sql}')
            db_connection()
    return cursor
