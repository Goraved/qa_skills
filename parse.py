import os
import sys
import webbrowser

from data import *
from helper import *
from html_creator import *

skills = get_skills()
skill_percent = {}
positions = get_positions()
ways = get_ways()
vacancy_links = get_vacancies()
total_info = []
print('Total count of vacancies - %s' % str(len(vacancy_links)))

# GO to each vacancy
for link in vacancy_links:
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
    skills = find_in_text(skills, vacancy_desciption)
    ways = find_in_text(ways, vacancy_title)
    position = find_in_text(positions, vacancy_title)
    total_info.append([[vacancy_link, vacancy_title], [company_link, company_title], city_title])
    # print(str(vacancy_links.index(link)) + ' of ' + str(len(vacancy_links)))
    progress = float(vacancy_links.index(link) / len(vacancy_links)) * 100
    sys.stdout.write("\r%d%%" % progress)
    sys.stdout.flush()

# Write to file
with open('style/index.html', 'w') as file:
    skills = order_dic_desc(skills)
    file.write(
        create_html(['Actual QA skills based on vacancies from DOU.ua', '(Total vacancies : %s)' % len(vacancy_links)]))
    file.write(create_table('SKILLS', ['Skill', 'Percent (%)', 'Count (#)']))
    for skill in skills:
        percent = str(round(float(skill[1] / len(vacancy_links)) * 100, 2)) + '%'
        if skill[1] > 0:
            file.write(add_table_row([skill[0], percent, skill[1]]))
            skill_percent.update({skill[0]: percent})
    file.write(close_table())

    # Write all links
    file.write(create_table('LINKS', ['Vacancy', 'Company', 'City']))
    for info in total_info:
        vacancy = create_link(info[0][0], info[0][1])
        company = create_link(info[1][0], info[1][1])
        file.write(add_table_row([vacancy, company, info[2]]))
    file.write(close_table())

    # Write all positions
    positions = order_dic_desc(positions)
    file.write(create_table('POSITIONS', ['Position', 'Count']))
    for position in positions:
        if position[1] > 0:
            file.write(add_table_row([position[0], str(position[1])]))
    file.write(close_table())

    # Write all ways
    ways = order_dic_desc(ways)
    file.write(create_table('WAYS', ['Way', 'Count']))
    for way in ways:
        if way[1] > 0:
            file.write(add_table_row([way[0], str(way[1])]))
    file.write(close_table())
    file.write(close_html())
webbrowser.open('file://' + os.path.realpath('style/index.html'))
save_statistics(skill_percent)
close_db()
