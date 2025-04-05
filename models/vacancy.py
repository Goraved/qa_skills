"""Module for working with vacancies"""
import logging
from datetime import date
from typing import List, Dict, Any

from data import query
from common_utils import (
    get_current_date_string,
    clear_records_by_date,
    batch_insert,
    delete_old_records
)

logger = logging.getLogger(__name__)

class Vacancy:
    """Vacancy container class"""
    def __init__(self):
        pass

    @staticmethod
    def delete_vacancies_older_than_month() -> None:
        """Delete vacancies older than a month"""
        delete_old_records('vacancies')

    @staticmethod
    def save_vacancies(values: List[Dict[str, str]], vac_skills: List[Dict[str, Any]]) -> None:
        """Save vacancy data"""
        # Get current date
        date_collected = get_current_date_string()

        # Delete previous data by current date
        clear_records_by_date('vacancies', date_collected)

        # Prepare skills lookup dictionary for faster access
        skills_lookup = {item['link']: item['skills'] for item in vac_skills}

        # Prepare batch insert data
        vac_list = []
        for result in values:
            # Skip empty results
            if not result:
                continue

            # Get skills for this vacancy
            link = result.get('vacancy_link', '')
            skills = skills_lookup.get(link, '')

            # Add to batch
            vac_list.append((
                result.get('vacancy_title', ''),
                link,
                result.get('company_title', ''),
                result.get('company_link', ''),
                result.get('city_title', ''),
                date_collected,
                skills
            ))

        # Execute batch insert
        if vac_list:
            batch_insert(
                'vacancies',
                ['vacancy', 'url', 'company', 'company_url', 'city', 'date_collected', 'skills'],
                vac_list
            )
            logger.info(f"Saved {len(vac_list)} vacancies")

def get_vacancies_by_skill(date_collected: str, skill: str) -> Dict[str, Any]:
    """Get vacancies by skill for a specific date"""
    vac = {'skill': skill}
    vacancies = []

    # Handle JavaScript specially (search for both JS and javascript)
    if skill.lower() in ('js', 'javascript'):
        # Create parameterized query with OR conditions
        skills_to_search = ['JS', 'javascript']
        where_clauses = []
        params = [date_collected]

        for js_skill in skills_to_search:
            where_clauses.extend([
                "(skills LIKE %s)",  # %|skill|%
                "(skills LIKE %s)",  # skill|%
                "(skills LIKE %s)",  # %|skill
                "(skills = %s)"      # skill
            ])
            params.extend([
                f'%|{js_skill}|%',
                f'{js_skill}|%',
                f'%|{js_skill}',
                js_skill
            ])

        where_str = " OR ".join(where_clauses)
        query_str = (
            "SELECT DISTINCT vacancy, url, company, city FROM vacancies "
            f"WHERE date_collected = %s AND ({where_str})"
        )

        rows = query(query_str, parameters=params)
    else:
        # Normal skill search
        params = [
            date_collected,
            f'%|{skill}|%',
            f'{skill}|%',
            f'%|{skill}',
            skill
        ]

        query_str = (
            "SELECT DISTINCT vacancy, url, company, city FROM vacancies "
            "WHERE date_collected = %s AND "
            "(skills LIKE %s OR skills LIKE %s OR skills LIKE %s OR skills = %s)"
        )

        rows = query(query_str, parameters=params)

    # Process results
    for row in rows:
        vacancies.append({
            'vacancy': row[0],
            'url': row[1],
            'company': row[2],
            'city': row[3]
        })

    vac['vacancies'] = vacancies
    return vac

class VacanciesStatistic:
    """Vacancy statistics container class"""
    def __init__(self, vacancy_title: str, vacancy_link: str, city_title: str,
                 company_title: str, company_link: str):
        self.city_title = city_title
        self.company_link = company_link
        self.company_title = company_title
        self.vacancy_link = vacancy_link
        self.vacancy_title = vacancy_title

def get_vacancies_statistics_by_date(date_collected: date) -> List[VacanciesStatistic]:
    """Get vacancy statistics for a specific date"""
    vacancies_stat = []

    rows = query(
        "SELECT vacancy, company, city, url, company_url FROM vacancies WHERE date_collected = %s",
        parameters=[date_collected]
    )

    for row in rows:
        vacancies_stat.append(VacanciesStatistic(
            vacancy_title=row[0],
            company_title=row[1],
            city_title=row[2],
            vacancy_link=row[3],
            company_link=row[4]
        ))

    return vacancies_stat