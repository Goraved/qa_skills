import random
import string
import threading

from flask import Flask, render_template, redirect, url_for

from parse import *

app = Flask(__name__)


class AsyncTask(threading.Thread):
    def __init__(self, task_id):
        super().__init__()
        self.task_id = task_id
        self.get_st = GetStat()

    def run(self):
        st = self.get_st.get_statistics()
        save_positions(st.positions)
        save_statistics(st.skill_percent, st.skills)
        save_ways(st.ways)
        save_vacancies(st.total_info)
        st.positions = {}
        st.ways = {}
        st.skill_percent = {}
        st.skills = {}
        st.total_info = []
        complete_task(self.task_id)


@app.route("/")
def main():
    return render_template('index.html')


# Start process of gathering statistics
@app.route('/get_stat', methods=['POST'])
def get_stat():
    task_id = ''.join([random.choice(string.digits) for _ in range(16)])
    create_task(task_id)
    async_task = AsyncTask(task_id=task_id)
    async_task.start()
    task_status_url = url_for('task_status', task_id=task_id)
    return task_id


@app.route('/TaskStatus/<int:task_id>')
def task_status(task_id):
    return get_task_state(task_id)


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
