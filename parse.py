import asyncio
import copy
import os
import re
from typing import List, Dict, Any, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed

import httpx
from lxml import html

from helper import find_in_text, headers
from models.position import get_positions
from models.skill import get_skills
from models.way import get_ways


class Stat:
    def __init__(self):
        self.total_info: List[Dict[str, str]] = []
        self.skills: Dict[str, int] = {}
        self.positions: Dict[str, int] = {}
        self.ways: Dict[str, int] = {}
        self.links: List[str] = []
        self.skill_percent: Dict[str, str] = {}


class GetStat:
    def __init__(self, max_workers: int = None):
        self.stat = Stat()
        self.count_of_vac = 0
        self.max_workers = max_workers or (os.cpu_count() or 1)

    async def get_statistics(self) -> Tuple[Stat, List[Dict[str, str]]]:
        """
        Retrieve and process vacancy statistics asynchronously.

        Returns:
            Tuple of Stat object and list of vacancy skills
        """
        try:
            # Concurrent async tasks for initial data retrieval
            # Ensure all these methods are async
            vacancy_links, skills, positions, ways = await asyncio.gather(
                self.async_get_vacancies(),
                get_skills(),
                get_positions(),
                get_ways()
            )

            self.stat.skills = skills
            self.stat.positions = positions
            self.stat.ways = ways
            self.count_of_vac = len(vacancy_links)

            # Use ProcessPoolExecutor for CPU-bound task of processing vacancies
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                # Prepare vacancy processing tasks
                vacancy_tasks = [
                    executor.submit(
                        self.vacancy_stats,
                        link.attrib.get('href'),
                        link.text
                    ) for link in vacancy_links
                ]

                # Collect results as they complete
                vacancy_info = []
                for future in as_completed(vacancy_tasks):
                    vacancy_info.append(future.result())

            self.merge_lists(vacancy_info)
            vac_skills = self.get_list_of_skills_in_vacancy(vacancy_info)

            return self.stat, vac_skills

        except Exception as e:
            print(f"Error in get_statistics: {e}")
            # Return empty stat and skills list in case of error
            return Stat(), []

    async def async_get_vacancies(self) -> List[html.HtmlElement]:
        """
        Asynchronously fetch vacancies.

        Returns:
            List of vacancy link elements
        """
        try:
            async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
                # Fetch initial page to get vacancies
                response = await client.get('https://jobs.dou.ua/vacancies/?category=QA')

                # Extract max count of vacancies
                max_count = int(html.fromstring(response.text).xpath('//h1')[0].text.split()[0])

                # Prepare for pagination
                vacancy_links = []
                urls = set()
                count = 0

                while len(vacancy_links) < max_count:
                    # Prepare data for XHR request
                    data = {
                        'csrfmiddlewaretoken': 'c6V5lBXwbscVXZdwSq7KTVYGI58dU0N0s1GFi0uWrRkw00Q4MLIyMKdBjFf3ob7e',
                        'count': count
                    }

                    # Make XHR request
                    xhr_response = await client.post(
                        'https://jobs.dou.ua/vacancies/xhr-load/',
                        data=data,
                        params=(('category', 'QA'), ('amp;city', '\u041A\u0438\u0435\u0432'))
                    )

                    # Parse links
                    links = html.fromstring(xhr_response.text).xpath('//div/a')

                    for link in links:
                        href = link.attrib.get('href')
                        if href not in urls:
                            vacancy_links.append(link)
                            urls.add(href)

                    count += 20

                return vacancy_links

        except Exception as e:
            print(f"Error fetching vacancies: {e}")
            return []

    def vacancy_stats(self, link: str, title: str) -> Stat:
        """
        Extract statistics for a single vacancy.

        Args:
            link: Vacancy link
            title: Vacancy title

        Returns:
            Stat object with vacancy information
        """
        try:
            stat = copy.deepcopy(self.stat)

            # Sanitize link
            clean_link = link.replace('\\', '').replace('"', "")

            # Use requests for synchronous HTTP request in ProcessPoolExecutor
            import requests

            # Fetch vacancy page
            vacancy = requests.get(clean_link.replace('?from=list_hot', ''), headers=headers)
            html_text = html.fromstring(vacancy.text)

            # Sanitize and decode title
            title = (title or '-- Couldn\'t parse title :(').encode('ascii').decode('unicode_escape')
            vacancy_title = title.replace('\\u00a0', ' ')

            # Extract company information
            company = html_text.xpath("//div[@class='info']//a[1]")
            if not company:
                try:
                    company_title = re.findall('companies/(.+)/vac', clean_link)[0].capitalize()
                    company_link = f'https://jobs.dou.ua/companies/{company_title}/vacancies'
                    company_title = company_title.encode('ascii').decode('unicode_escape')
                except IndexError:
                    company_title = '-- Couldn\'t parse company :('
                    company_link = ''
            else:
                company_title = (company[0].text or '-- Couldn\'t parse company :(').replace('\\u00a0', ' ')
                company_link = company[0].get('href', '').replace('\\', '').replace('"', "")

            # Extract city
            try:
                city_title = html_text.xpath("//div[@class='sh-info']/span")[0].text
            except (IndexError, AttributeError):
                city_title = '-- Couldn\'t parse city :('

            # Combine description from paragraphs and list items
            description_parts = html_text.xpath("//div[@class='l-vacancy']//p | //div[@class='l-vacancy']//ul/li")
            vacancy_description = ''.join(''.join(part.itertext()) for part in description_parts)

            # Update statistics
            stat.skills = find_in_text(stat.skills, vacancy_description, vacancy_title)
            stat.ways = find_in_text(stat.ways, vacancy_title)
            stat.position = find_in_text(stat.positions, vacancy_title)

            # Store vacancy information
            stat.total_info = {
                'vacancy_link': clean_link.strip(),
                'vacancy_title': vacancy_title.strip(),
                'company_link': company_link.strip(),
                'company_title': company_title.strip(),
                'city_title': city_title.strip()
            }

            return stat

        except Exception as e:
            print(f"Error processing vacancy {link}: {e}")
            return copy.deepcopy(self.stat)

    # Rest of the methods remain the same as in the previous implementation