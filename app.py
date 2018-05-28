from flask import Flask, render_template, redirect

from parse import *

app = Flask(__name__)


@app.route("/")
def main():
    return render_template('index.html')


# Start process of gathering statistics
@app.route('/get_stat', methods=['POST'])
def get_stat():
    get_statistics()
    return redirect('/save_data')


# Get list of all vacancies
def get_vac():
    cur = query('Select * from technical where id = 2 ')
    for row in cur.fetchall():
        vacancies_taken = row[0]
    if vacancies_taken != 0:
        query('Update technical set result = 1 where id = 2')
        return get_vacancies()


@app.route('/save_data')
def save_data():
    save_positions(Stat.positions)
    save_statistics(Stat.skill_percent, Stat.skills)
    save_ways(Stat.ways)
    return redirect('/statistics')


@app.route("/statistics")
def show_statistics():
    links = Stat.total_info
    positions = get_latest_positions_statistics()
    ways = get_latest_ways_statistics()
    stats = get_latest_statistics()
    return render_template('statistics.html', links=links, stats=stats, positions=positions, ways=ways)


if __name__ == "__main__":
    app.run()
