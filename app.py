import celery as celery
from flask import Flask, render_template, redirect, url_for

from parse import *

app = Flask(__name__)


@app.route("/")
def main():
    return render_template('index.html')


# Start process of gathering statistics
@app.route('/get_stat', methods=['POST'])
def get_stat():
    save_data.delay()
    # return redirect(url_for('save_data'))


# Get list of all vacancies
def get_vac():
    return get_vacancies()


# @app.route('/save_data')
@celery.task(bind=True)
def save_data():
    get_statistics()
    save_positions(Stat.positions)
    save_statistics(Stat.skill_percent, Stat.skills)
    save_ways(Stat.ways)
    save_vacancies(Stat.total_info)
    Stat.positions = {}
    Stat.ways = {}
    Stat.skill_percent = {}
    Stat.skills = {}
    Stat.total_info = []
    return redirect(url_for('show_statistics'))


@app.route("/statistics")
def show_statistics():
    links = get_latest_vacancies_statistics()
    positions = get_latest_positions_statistics()
    ways = get_latest_ways_statistics()
    stats = get_latest_statistics()
    tech = [{'vac_count': len(links), 'date_collected': stats[0]['date']}]
    return render_template('statistics.html', links=links, stats=stats, positions=positions, ways=ways, tech=tech)


if __name__ == "__main__":
    app.run()
