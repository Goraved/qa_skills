import pytest

from index import create_app
from models.statistic import Statistic


@pytest.fixture(scope="session")
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app


endpoints = ['/', '/skill', '/statistics', '/get_statistics', '/get_language_comparison', '/skill/10']


@pytest.mark.parametrize('url', endpoints)
def test_get_endpoints(client, url):
    assert client.get(url).status_code == 200


def test_skill_vacancies(client):
    dates = Statistic.get_str_dates()
    # 10 = python
    assert client.get(f'/skill_vacancies/10_{dates[2]}').status_code == 200


def test_statistic_by_date(client):
    dates = Statistic.get_str_dates()
    assert client.get(f'/statistic/{dates[2]}').status_code == 200


def test_get_stats(client):
    assert client.post('/get_stat').status_code == 200
