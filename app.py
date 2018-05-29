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
    return get_vacancies()


@app.route('/save_data')
def save_data():
    save_positions(Stat.positions)
    save_statistics(Stat.skill_percent, Stat.skills)
    save_ways(Stat.ways)
    save_vacancies(Stat.total_info)
    Stat.positions = None
    Stat.ways = None
    Stat.skill_percent = None
    Stat.skills = None
    return redirect('/statistics')


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
