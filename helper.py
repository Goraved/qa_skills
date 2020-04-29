import asyncio
import os
import re

import requests
from lxml import html

from data import set_cached_data, clear_plt

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 OPR/50.0.2762.67',
    'Referer': 'https://jobs.dou.ua/vacancies/?city=%D0%9A%D0%B8%D0%B5%D0%B2&category=QA',
    'X-Requested-With': 'XMLHttpRequest'
}


def find_in_text(list_item, text, vacancy_title=''):
    for item in list_item:
        if item in ['C#', '.Net'] and (item in text or item in vacancy_title):
            list_item[item] += 1
            continue
        if re.search(r"\b" + re.escape(item) + r"\b", text, re.IGNORECASE) is not None:
            list_item[item] += 1
        elif re.search(r"\b" + re.escape(item) + r"\b", vacancy_title, re.IGNORECASE) is not None:
            list_item[item] += 1
    return list_item


def order_dic_desc(dictionary):
    items = [(v, k) for k, v in dictionary.items()]
    items.sort()
    items.reverse()  # so largest is first
    return [(k, v) for v, k in items]


async def get_vacancies():
    await asyncio.sleep(0)
    cookies = {
        'csrftoken': 'JzvFajkcrm5YnSCZ0reV47uW4jO1IhKfZugf7IRCHLdzqTfxUMPJXWJRFTVRcs4t',
        '_ga': 'GA1.2.1912596478.1516990675',
        '_gid': 'GA1.2.1332076466.1516990675',
        '_gat': '1',
    }

    params = (
        ('category', 'QA'),
        ('amp;city', '\u041A\u0438\u0435\u0432'),
    )
    vacancy_links = []

    count = 0

    max_count = 500
    urls = []
    while len(vacancy_links) <= max_count and count < 600:
        data = [
            ('csrfmiddlewaretoken', 'c6V5lBXwbscVXZdwSq7KTVYGI58dU0N0s1GFi0uWrRkw00Q4MLIyMKdBjFf3ob7e'),
            ('count', count),
        ]

        response = requests.post('https://jobs.dou.ua/vacancies/xhr-load/', headers=headers, params=params,
                                 cookies=cookies, data=data)
        # Get vacancy links
        links = html.fromstring(response.text).xpath('//div/a')

        for link in links:
            if link.attrib.get('href') not in urls:
                vacancy_links.append(link)
                urls.append(link.attrib.get('href'))
        count += 20
    return vacancy_links


def clear_cached_data():
    set_cached_data(None)
    if os.path.exists('static/images/graph.png'):
        os.remove('static/images/graph.png')
    clear_plt()
    if os.path.exists('static/images/languages.png'):
        os.remove('static/images/languages.png')
