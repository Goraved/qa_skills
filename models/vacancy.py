import asyncio
import time
from datetime import date
from typing import List

from data import query


class Vacancy:
    def __init__(self):
        pass

    @staticmethod
    async def delete_vacancies_older_than_month():
        await asyncio.sleep(0)
        query("DELETE FROM vacancies WHERE date_collected < NOW() - interval 31 DAY")

    @staticmethod
    def save_vacancies(values: list, vac_skills: dict):
        # Get current date
        date_collected = time.strftime('%Y-%m-%d')
        # Delete previous data by current date
        query(f"Delete FROM vacancies WHERE date_collected = '{date_collected}'")
        vac_list = []
        for result in values:
            # Save vacancies
            if not result:
                continue
            skills = [_['skills'] for _ in vac_skills if _['link'] in result['vacancy_link']][0]
            vac_list.append(
                (result['vacancy_title'], result['vacancy_link'], result['company_title'], result['company_link'],
                 result['city_title'], date_collected, skills))
        insert_query = "Insert into vacancies (vacancy, url, company, company_url, city, date_collected, skills) " \
                       "values (%s, %s, %s, %s, %s, %s, %s);"
        query(insert_query, parameters=vac_list, many=True)


def get_vacancies_by_skill(date_collected: str, skill):
    vac = {'skill': skill}
    vacancies = []
    if skill in ('JS', 'javascript'):
        for js_skill in ('JS', 'javascript'):
            cur = query(
                f"SELECT distinct vacancy, url, company, city FROM vacancies WHERE date_collected = '{date_collected}' "
                f"and (skills like '%|{js_skill}|%' OR skills like '{js_skill}|%' "
                f"OR skills like '%|{js_skill}' OR skills like '{js_skill}')")
            for row in cur.fetchall():
                vacancies.append({'vacancy': row[0], 'url': row[1], 'company': row[2], 'city': row[3]})
    else:
        cur = query(
            f"SELECT distinct vacancy, url, company, city FROM vacancies WHERE date_collected = '{date_collected}' "
            f"and (skills like '%|{skill}|%' OR skills like '{skill}|%' "
            f"OR skills like '%|{skill}' OR skills like '{skill}')")
        for row in cur.fetchall():
            vacancies.append({'vacancy': row[0], 'url': row[1], 'company': row[2], 'city': row[3]})
    vac['vacancies'] = vacancies
    return vac


class VacanciesStatistic:
    def __init__(self, vacancy_title: str, vacancy_link: str, city_title: str, company_title: str, company_link: str):
        self.city_title = city_title
        self.company_link = company_link
        self.company_title = company_title
        self.vacancy_link = vacancy_link
        self.vacancy_title = vacancy_title


async def get_vacancies_statistics_by_date(date_collected: date) -> List[VacanciesStatistic]:
    await asyncio.sleep(0)
    vacancies_stat = []
    cur = query(f"SELECT *  FROM vacancies WHERE date_collected = '{date_collected}';")
    for row in cur.fetchall():
        vacancies_stat.append(VacanciesStatistic(vacancy_title=row[1], vacancy_link=row[4], company_title=row[2],
                                                 company_link=row[6], city_title=row[3]))
    return vacancies_stat
