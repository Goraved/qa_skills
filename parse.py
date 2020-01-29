import copy
import multiprocessing as mp

from data import *
from helper import *


class Stat:
    total_info = []
    skills = {}
    positions = {}
    ways = {}
    links = []
    skill_percent = {}


class GetStat:
    def __init__(self):
        self.st = Stat()
        self.count_of_vac = 0

    def get_statistics(self):
        ioloop = asyncio.new_event_loop()
        asyncio.set_event_loop(ioloop)
        tasks = [get_vacancies(), get_skills(), get_positions(), get_ways()]
        async_values = ioloop.run_until_complete(asyncio.gather(*tasks))
        vacancy_links = async_values[0]
        self.st.skills = async_values[1]
        self.st.positions = async_values[2]
        self.st.ways = async_values[3]
        self.count_of_vac = len(vacancy_links)
        ioloop.close()
        # GO to each vacancy
        # pool = mp.Pool(mp.cpu_count())
        pool = mp.Pool(8)
        result = pool.starmap(self.vacancy_stats, [(link.attrib.get('href'), link.text, self.count_of_vac) for link in
                                                   vacancy_links])
        self.merge_lists(result)
        pool.close()
        del result
        return self.st

    def vacancy_stats(self, link, title, count_of_vacancies):
        st = copy.deepcopy(self.st)
        vacancy = requests.get(link.replace('\\', '').replace('"', ""), headers=headers)
        # Get vacancy link and title
        if not title:
            title = '-- Couldn\'t parse title :('
        vacancy_title = title.replace('\\u00a0', ' ')
        vacancy_link = link.replace('\\', '').replace('"', "")
        # Get company link and title
        company = html.fromstring(vacancy.text).xpath("//div[@class='info']/div/a[1]")
        if not company:
            return st
        if not company[0].text:
            company[0].text = '-- Couldn\'t parse company :('
        company_title = company[0].text.replace('\\u00a0', ' ')
        company_link = company[0].get('href').replace('\\', '').replace('"', "")
        try:
            city = html.fromstring(vacancy.text).xpath("//div[@class='sh-info']/span")
            city_title = city[0].text
        except:
            city_title = '-- Couldn\'t parse city :('

        # Get all html paragraphs
        description = html.fromstring(vacancy.text).xpath("//div[@class='l-vacancy']//p")
        vacancy_desciption = ''
        # Parse text from all paragraph into one
        for paragraph in description:
            vacancy_desciption += "".join([x for x in paragraph.itertext()])
        # Search each skill in vacancy
        st.skills = find_in_text(st.skills, vacancy_desciption)
        st.ways = find_in_text(st.ways, vacancy_title)
        st.position = find_in_text(st.positions, vacancy_title)
        st.total_info = {'vacancy_link': vacancy_link, 'vacancy_title': vacancy_title, 'company_link': company_link,
                         'company_title': company_title, 'city_title': city_title}
        return st

    def merge_lists(self, results):
        positions = [_.positions for _ in results]
        skills = [_.skills for _ in results]
        ways = [_.ways for _ in results]
        self.st.positions = {k: sum(d[k] for d in positions) for k in positions[0]}
        self.st.skills = {k: sum(d[k] for d in skills) for k in skills[0]}
        self.st.ways = {k: sum(d[k] for d in ways) for k in ways[0]}
        for skill in self.st.skills:
            percent = str(round(float(self.st.skills[skill] / self.count_of_vac) * 100, 2)) + '%'
            if self.st.skills[skill] > 0:
                self.st.skill_percent.update({skill: percent})
        self.st.total_info = [_.total_info for _ in results]
