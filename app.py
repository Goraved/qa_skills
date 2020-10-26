import asyncio
import os
import random
import string
import threading
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, request, jsonify

from data import set_cached_data, get_cached_data
from graphs import get_stats, get_languages_comparison, get_skill_stats, clear_plt
from helper import clear_cached_data
from models.position import Position
from models.skill import get_skill_list
from models.statistic import Statistic
from models.task import Task
from models.vacancy import Vacancy, get_vacancies_by_skill
from models.way import Way
from parse import GetStat, Stat

app = Flask(__name__)


class AsyncTask(threading.Thread):
    def __init__(self, task_id):
        super().__init__()
        self.task_id = task_id
        self.get_st = GetStat()

    def run(self):
        stat, vac_skills = self.get_st.get_statistics()
        Position.save_positions(stat.positions)
        Statistic.save_statistics(stat.skill_percent, stat.skills)
        Way.save_ways(stat.ways)
        Vacancy.save_vacancies(stat.total_info, vac_skills)
        clear_cached_data()
        stat.positions = {}
        stat.ways = {}
        stat.skill_percent = {}
        stat.skills = {}
        stat.total_info = []
        iloop = asyncio.new_event_loop()
        asyncio.set_event_loop(iloop)
        tasks = [Task(self.task_id).complete_task(), Statistic.delete_stats_older_than_month(),
                 Vacancy.delete_vacancies_older_than_month(),
                 Way.delete_ways_older_than_month(), Position.delete_positions_older_than_month()]
        iloop.run_until_complete(asyncio.wait(tasks))


@app.route("/")
def main():
    return render_template('index.html')


# Start process of gathering statistics
@app.route('/get_stat', methods=['POST'])
def get_stat():
    task_id = ''.join([random.choice(string.digits) for _ in range(16)])
    Task(task_id).create_task()
    async_task = AsyncTask(task_id=task_id)
    async_task.start()
    url_for('task_status', task_id=task_id)
    return task_id


@app.route('/TaskStatus/<int:task_id>')
def task_status(task_id):
    return Task(task_id).get_task_state()


@app.route('/save_data')
def save_data():
    Stat.positions = {}
    Stat.ways = {}
    Stat.skill_percent = {}
    Stat.skills = {}
    Stat.total_info = []
    return redirect(url_for('show_statistics'))


# STATS
@app.route("/statistics")
def show_latest_statistics():
    dates = Statistic.get_dates()
    info = get_stats(dates[0])
    set_cached_data(dict(stats=[vars(_) for _ in info[1]], positions=[vars(_) for _ in info[2]],
                         ways=[vars(_) for _ in info[3]]))
    return render_template('statistics.html', links=info[0], stats=info[1], positions=info[2], ways=info[3],
                           tech=info[4], dates=dates)


@app.route("/get_statistics", methods=['GET'])
def get_latest_statistics_endpoint():
    if get_cached_data():
        cached_data = jsonify(get_cached_data())
    else:
        dates = Statistic.get_dates()
        info = get_stats(dates[0])
        # Class objects to dict
        cached_data = dict(stats=[vars(_) for _ in info[1]], positions=[vars(_) for _ in info[2]],
                           ways=[vars(_) for _ in info[3]])
        set_cached_data(cached_data)
        cached_data = jsonify(cached_data)
    return cached_data


@app.route("/get_language_comparison", methods=['GET'])
def get_language_comparison_endpoint():
    if not os.path.isfile('./static/images/languages.png'):
        get_languages_comparison()
    rand = str(datetime.now()).replace(' ', '_')
    return jsonify({'image': os.path.abspath(f'./static/images/languages.png?v={rand}')})


@app.route("/statistic/<date>")
def show_specific_statistics(date):
    dates = Statistic.get_str_dates()
    try:
        info = get_stats(date)
        return render_template('statistics.html', links=info[0], stats=info[1], positions=info[2], ways=info[3],
                               tech=info[4], dates=dates)
    except IndexError:
        return render_template('error.html', tech=[{'date_collected': date}])


# SKILLS
@app.route("/skill")
def show_stats_by_skill():
    clear_graph()
    info = get_skill_stats(10)
    return render_template('skill.html', skills=info[1], stats=info[0], selected_skill=info[2])


@app.route("/skill/<skill_id>")
def show_stats_by_specific_skill(skill_id):
    info = get_skill_stats(int(skill_id))
    return render_template('skill.html', skills=info[1], stats=info[0], selected_skill=info[2])


@app.route("/clear_graph")
def clear_graph():
    if os.path.exists('static/images/graph.png'):
        os.remove('static/images/graph.png')
    clear_plt()
    link = redirect_url()
    if link:
        return redirect(link)
    else:
        return redirect(url_for('show_stats_by_skill'))


def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer


# VACANCIES
@app.route('/get_vac', methods=['POST'])
def get_vac():
    skill_id = request.form['skill_id']
    date = request.form['date']
    return redirect(f'/skill_vacancies/{skill_id}_{date}')


@app.route("/skill_vacancies/<skill_id>_<date>")
def show_vacancies_by_specific_skill(skill_id, date):
    dates = Statistic.get_str_dates()
    skills = get_skill_list()
    selected = [_ for _ in skills if _['id'] == int(skill_id)][0]
    vacancies = get_vacancies_by_skill(date, selected['name'])['vacancies']
    return render_template('skill_vacancies.html', skills=skills, vacancies=vacancies, selected_skill=[selected],
                           dates=dates, tech=[{'date_collected': date}])


@app.route("/skill_vacancies")
def show_vacancies_by_skill():
    dates = Statistic.get_str_dates()
    skills = get_skill_list()
    selected = [_['id'] for _ in skills if _['id'] == 10][0]
    vacancies = get_vacancies_by_skill(dates[0], selected['name'])['vacancies']
    return render_template('skill_vacancies.html', skills=skills, vacancies=vacancies, selected_skill=[selected],
                           dates=dates, tech=[{'date_collected': dates[0]}])


# ERRORS
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', title='404'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('500.html', title='500'), 500


if __name__ == "__main__":
    app.run()


def create_app():
    return app
