import asyncio
import os
import re
from typing import List, Dict, Tuple

import httpx
from lxml import html

from data import set_cached_data
from graphs import clear_plt

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/63.0.3239.132 Safari/537.36 OPR/50.0.2762.67',
    'Referer': 'https://jobs.dou.ua/vacancies/?city=%D0%9A%D0%B8%D0%B5%D0%B2&category=QA',
    'X-Requested-With': 'XMLHttpRequest'
}


def find_in_text(list_item: Dict[str, int], text: str, vacancy_title: str = '') -> Dict[str, int]:
    """
    Find occurrences of items in text or vacancy title.

    Args:
        list_item: Dictionary of items to search for
        text: Full text to search in
        vacancy_title: Title of the vacancy to search in

    Returns:
        Updated dictionary with item counts
    """
    for item in list_item:
        # Special handling for C# and .Net
        if item in ['C#', '.Net'] and (item in text or item in vacancy_title):
            list_item[item] += 1
            continue

        # Case-insensitive whole word search
        if (re.search(r"\b" + re.escape(item) + r"\b", text, re.IGNORECASE) is not None or
                re.search(r"\b" + re.escape(item) + r"\b", vacancy_title, re.IGNORECASE) is not None):
            list_item[item] += 1
    return list_item


def order_dic_desc(dictionary: Dict[str, int]) -> List[Tuple[str, int]]:
    """
    Order dictionary by values in descending order.

    Args:
        dictionary: Input dictionary to be sorted

    Returns:
        Sorted list of (key, value) tuples
    """
    return sorted(dictionary.items(), key=lambda x: x[1], reverse=True)


async def get_vacancies(timeout: float = 10.0) -> List[html.HtmlElement]:
    """
    Asynchronously fetch vacancies from Dou.ua.

    Args:
        timeout: Request timeout in seconds

    Returns:
        List of vacancy link elements
    """
    async with httpx.AsyncClient(
            headers=headers,
            timeout=httpx.Timeout(timeout),
            follow_redirects=True
    ) as client:
        # Initial GET request to get max count of vacancies
        dou_info = await client.get('https://jobs.dou.ua/vacancies/?category=QA')
        max_count = int(html.fromstring(dou_info.text).xpath('//h1')[0].text.split()[0])

        # Set up tracking to avoid duplicate links
        vacancy_links = []
        urls = set()

        count = 0
        while len(vacancy_links) < max_count:
            # Async post request for loading more vacancies
            data = {
                'csrfmiddlewaretoken': 'c6V5lBXwbscVXZdwSq7KTVYGI58dU0N0s1GFi0uWrRkw00Q4MLIyMKdBjFf3ob7e',
                'count': count
            }

            response = await client.post(
                'https://jobs.dou.ua/vacancies/xhr-load/',
                data=data,
                params=(('category', 'QA'), ('amp;city', '\u041A\u0438\u0435\u0432'))
            )

            # Parse links
            links = html.fromstring(response.text).xpath('//div/a')

            for link in links:
                href = link.attrib.get('href')
                if href not in urls:
                    vacancy_links.append(link)
                    urls.add(href)

            count += 20

        return vacancy_links


def clear_cached_data():
    """
    Clear cached data and remove generated image files.
    """
    set_cached_data({})

    # List of files to remove
    files_to_remove = [
        'static/images/graph.png',
        'static/images/languages.png'
    ]

    for file_path in files_to_remove:
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass

    clear_plt()