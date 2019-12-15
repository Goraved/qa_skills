import random
import string
import threading

from flask import Flask, render_template, redirect, url_for

from parse import *

app = Flask(__name__)

tasks = {}


class AsyncTask(threading.Thread):
    def __init__(self, task_id):
        super().__init__()
        self.task_id = task_id
        tasks[task_id] = 'False'

    def run(self):
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
        tasks[self.task_id] = 'True'


@app.route("/")
def main():
    return render_template('index.html')


# Start process of gathering statistics
@app.route('/get_stat', methods=['POST'])
def get_stat():
    task_id = ''.join([random.choice(string.digits) for _ in range(16)])
    async_task = AsyncTask(task_id=task_id)
    async_task.start()
    task_status_url = url_for('task_status', task_id=task_id)
    return task_id


@app.route('/TaskStatus/<int:task_id>')
def task_status(task_id):
    return tasks[str(task_id)]


# Get list of all vacancies
def get_vac():
    return get_vacancies()


@app.route('/save_data')
def save_data():
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
