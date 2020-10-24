import asyncio
import copy
import multiprocessing as mp
import re

import requests
from lxml import html

from helper import get_vacancies, headers, find_in_text
from models.position import get_positions
from models.skill import get_skills
from models.way import get_ways


class Stat:
    total_info = []
    skills = {}
    positions = {}
    ways = {}
    links = []
    skill_percent = {}


class GetStat:
    def __init__(self):
        self.stat = Stat()
        self.count_of_vac = 0

    def get_statistics(self):
        ioloop = asyncio.new_event_loop()
        asyncio.set_event_loop(ioloop)
        tasks = [get_vacancies(), get_skills(), get_positions(), get_ways()]
        async_values = ioloop.run_until_complete(asyncio.gather(*tasks))
        vacancy_links = async_values[0]
        self.stat.skills = async_values[1]
        self.stat.positions = async_values[2]
        self.stat.ways = async_values[3]
        self.count_of_vac = len(vacancy_links)
        ioloop.close()
        # GO to each vacancy
        pool = mp.Pool(mp.cpu_count())
        result = pool.starmap(self.vacancy_stats, [(link.attrib.get('href'), link.text) for link in
                                                   vacancy_links])
        self.merge_lists(result)
        vac_skills = self.get_list_of_skills_in_vacancy(result)

        pool.close()
        del result
        return self.stat, vac_skills

    def vacancy_stats(self, link: str, title: str) -> Stat:
        stat = copy.deepcopy(self.stat)
        vacancy = requests.get(link.replace('\\', '').replace('"', ""), headers=headers)
        # html_text = html.fromstring(vacancy.text)
        html_text = html.fromstring(vacancy.content)
        # Get vacancy link and title
        if not title:
            title = '-- Couldn\'t parse title :('
        title = title.encode('ascii').decode('unicode_escape')
        vacancy_title = title.replace('\\u00a0', ' ')
        vacancy_link = link.replace('\\', '').replace('"', "").replace('?from=list_hot', '')
        # Get company link and title
        company = html_text.xpath("//div[@class='info']//a[1]")
        if not company:
            company_title = re.findall('companies/(.+)/vac', vacancy_link)[0].capitalize()
            company_link = f'https://jobs.dou.ua/companies/{company_title}/vacancies'
            company_title = company_title.encode('ascii').decode('unicode_escape')
        else:
            if not company[0].text:
                company[0].text = '-- Couldn\'t parse company :('
            company_title = company[0].text.replace('\\u00a0', ' ')
            company_link = company[0].get('href').replace('\\', '').replace('"', "")
        try:
            city = html_text.xpath("//div[@class='sh-info']/span")
            city_title = city[0].text
        except:
            city_title = '-- Couldn\'t parse city :('

        # Get all html paragraphs
        description = html_text.xpath("//div[@class='l-vacancy']//p")
        vacancy_description = ''
        # Parse text from all paragraph into one
        for paragraph in description:
            vacancy_description += "".join(paragraph.itertext())
        # Search each skill in vacancy
        stat.skills = find_in_text(stat.skills, vacancy_description, vacancy_title)
        stat.ways = find_in_text(stat.ways, vacancy_title)
        stat.position = find_in_text(stat.positions, vacancy_title)
        stat.total_info = {'vacancy_link': vacancy_link, 'vacancy_title': vacancy_title, 'company_link': company_link,
                           'company_title': company_title, 'city_title': city_title}
        return stat

    def merge_lists(self, results):
        positions = [_.positions for _ in results]
        skills = [_.skills for _ in results]
        ways = [_.ways for _ in results]
        self.stat.positions = {k: sum(d[k] for d in positions) for k in positions[0]}
        self.stat.skills = {k: sum(d[k] for d in skills) for k in skills[0]}
        self.stat.ways = {k: sum(d[k] for d in ways) for k in ways[0]}
        self.merge_js()
        for skill in self.stat.skills:
            percent = str(round(float(self.stat.skills[skill] / self.count_of_vac) * 100, 2)) + '%'
            if self.stat.skills[skill] > 0:
                self.stat.skill_percent.update({skill: percent})
        self.stat.total_info = [_.total_info for _ in results]

    def merge_js(self):
        self.stat.skills['javascript'] += self.stat.skills['JS']
        del self.stat.skills['JS']

    @staticmethod
    def get_list_of_skills_in_vacancy(results):
        vacancies_skills = []
        for vacancy in results:
            if not vacancy.total_info:
                continue
            skills = '|'.join([skill[0] for skill in vacancy.skills.items() if skill[1] > 0])
            vacancies_skills.append({'link': vacancy.total_info['vacancy_link'], 'skills': skills})
        return vacancies_skills
