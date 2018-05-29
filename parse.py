from data import *
from helper import *


class Stat:
    total_info = []
    skills = {}
    positions = {}
    ways = {}
    links = []
    skill_percent = {}


def get_statistics():
    vacancy_links = get_vacancies()
    Stat.skills = get_skills()
    Stat.positions = get_positions()
    Stat.ways = get_ways()
    # GO to each vacancy
    for index, link in enumerate(vacancy_links):
        vacancy = requests.get(link.attrib.get('href').replace('\\', '').replace('"', ""), headers=headers)
        # Get vacancy link and title
        vacancy_title = link.text.replace('\\u00a0', ' ')
        vacancy_link = link.attrib.get('href').replace('\\', '').replace('"', "")
        # Get company link and title
        company = html.fromstring(vacancy.text).xpath("//div[@class='info']/div/a[1]")
        company_title = company[0].text.replace('\\u00a0', ' ')
        company_link = company[0].get('href').replace('\\', '').replace('"', "")
        try:
            city = html.fromstring(vacancy.text).xpath("//div[@class='sh-info']/span")
            city_title = city[0].text
        except:
            city = None

        # Get all html paragraphs
        description = html.fromstring(vacancy.text).xpath("//div[@class='l-vacancy']//p")
        vacancy_desciption = ''
        # Parse text from all paragraph into one
        for paragraph in description:
            vacancy_desciption += "".join([x for x in paragraph.itertext()])
        # Search each skill in vacancy
        Stat.skills = find_in_text(Stat.skills, vacancy_desciption)
        Stat.ways = find_in_text(Stat.ways, vacancy_title)
        Stat.position = find_in_text(Stat.positions, vacancy_title)
        Stat.total_info.append(
            {'vacancy_link': vacancy_link, 'vacancy_title': vacancy_title, 'company_link': company_link,
             'company_title': company_title, 'city_title': city_title})
        for skill in Stat.skills:
            percent = str(round(float(Stat.skills[skill] / len(vacancy_links)) * 100, 2)) + '%'
            if Stat.skills[skill] > 0:
                Stat.skill_percent.update({skill: percent})
