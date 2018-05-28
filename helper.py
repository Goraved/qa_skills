import os
import re

import requests
from lxml import html

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 OPR/50.0.2762.67',
    'Referer': 'https://jobs.dou.ua/vacancies/?city=%D0%9A%D0%B8%D0%B5%D0%B2&category=QA',
    'X-Requested-With': 'XMLHttpRequest'
}


def find_in_text(list_item, text):
    for item in list_item:
        if re.search(re.escape(item), text, re.IGNORECASE) is not None:
            list_item[item] += 1
    return list_item


def order_dic_desc(dictionary):
    items = [(v, k) for k, v in dictionary.items()]
    items.sort()
    items.reverse()  # so largest is first
    return [(k, v) for v, k in items]


def get_vacancies():
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
    if os.environ['app_type'] == 'remote':
        max_count = 20
    else:
        max_count = 10
    while len(vacancy_links) <= max_count:
        data = [
            ('csrfmiddlewaretoken', 'c6V5lBXwbscVXZdwSq7KTVYGI58dU0N0s1GFi0uWrRkw00Q4MLIyMKdBjFf3ob7e'),
            ('count', count),
        ]

        response = requests.post('https://jobs.dou.ua/vacancies/xhr-load/', headers=headers, params=params,
                                 cookies=cookies,
                                 data=data)
        # Get vacancy links
        vacancy_links += html.fromstring(response.text).xpath('//div/a')
        count += 20
    return vacancy_links
