import asyncio
import os
import random
import string
import threading
from datetime import datetime
from typing import Dict, Any

from flask import Flask, render_template, redirect, url_for, request, jsonify, abort

from data import set_cached_data, get_cached_data
from graphs import get_stats, get_languages_comparison, get_skill_stats, clear_plt
from helper import clear_cached_data
from models.position import Position
from models.skill import get_skill_list
from models.statistic import Statistic
from models.task import Task
from models.vacancy import Vacancy, get_vacancies_by_skill
from models.way import Way
from parse import GetStat

app = Flask(__name__)


class AsyncTask(threading.Thread):
    def __init__(self, task_id: str):
        super().__init__()
        self.task_id = task_id
        self.get_st = GetStat()
        self.result: Dict[str, Any] = {"status": "pending"}
        self.exception: Exception = None

    def run(self):
        """
        Run the async task synchronously using asyncio
        """
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Run the async method synchronously
            stat, vac_skills = loop.run_until_complete(self.get_st.get_statistics())

            # Update task status
            task = Task(self.task_id)

            # Check if we actually got any data
            if not stat.total_info:
                loop.run_until_complete(task.fail_task("No vacancies found"))
                self.result = {"status": "failed", "error": "No vacancies found"}
                return

            # Process the results
            try:
                Position.save_positions(stat.positions)
                Statistic.save_statistics(stat.skill_percent, stat.skills)
                Way.save_ways(stat.ways)
                Vacancy.save_vacancies(stat.total_info, vac_skills)
                clear_cached_data()
            except Exception as save_error:
                loop.run_until_complete(task.fail_task(str(save_error)))
                self.result = {"status": "failed", "error": str(save_error)}
                return

            # Delete unnecessary data
            stat.positions.clear()
            stat.ways.clear()
            stat.skill_percent.clear()
            stat.skills.clear()
            stat.total_info.clear()

            # Run additional async tasks
            async def cleanup_tasks():
                try:
                    await asyncio.gather(
                        task.complete_task(),
                        Statistic.delete_stats_older_than_month(),
                        Vacancy.delete_vacancies_older_than_month(),
                        Way.delete_ways_older_than_month(),
                        Position.delete_positions_older_than_month()
                    )
                except Exception as cleanup_error:
                    await task.fail_task(str(cleanup_error))

            loop.run_until_complete(cleanup_tasks())

            # Mark task as completed
            self.result = {"status": "completed"}

        except Exception as e:
            # Log the exception
            print(f"Unhandled error in AsyncTask: {e}")
            self.exception = e

            # Mark task as failed
            try:
                task = Task(self.task_id)
                loop.run_until_complete(task.fail_task(str(e)))
            except Exception as task_error:
                print(f"Error marking task as failed: {task_error}")

            self.result = {"status": "failed", "error": str(e)}
        finally:
            # Always close the event loop
            try:
                loop.close()
            except Exception as close_error:
                print(f"Error closing event loop: {close_error}")


@app.route("/")
def main():
    return render_template('index.html')


# Start process of gathering statistics
@app.route('/get_stat', methods=['POST'])
def get_stat():
    # Generate a unique task ID
    task_id = ''.join(random.choices(string.digits, k=16))  # Generate 16-digit task ID

    # Create and start the task
    Task(task_id).create_task()
    async_task = AsyncTask(task_id=task_id)
    async_task.start()

    # Redirect to task status
    return task_id


@app.route('/TaskStatus/<task_id>')
def task_status(task_id):
    """
    Check the status of a task
    """
    try:
        # Retrieve task state from database
        status = Task(task_id).get_task_state()
        return status

    except Exception as e:
        print(f"Error in task_status: {e}")
        return "error"


@app.route('/save_data')
def save_data():
    """
    Clear statistical data
    """
    # Instead of using global Stat, clear the data
    clear_cached_data()
    return redirect(url_for('show_latest_statistics'))


# STATS
@app.route("/statistics")
def show_latest_statistics():
    dates = Statistic.get_dates()
    info = get_stats(dates[0])
    set_cached_data(dict(
        stats=[vars(_) for _ in info[1]],
        positions=[vars(_) for _ in info[2]],
        ways=[vars(_) for _ in info[3]]
    ))
    return render_template('statistics.html',
        links=info[0],
        stats=info[1],
        positions=info[2],
        ways=info[3],
        tech=info[4],
        dates=dates
    )


@app.route("/get_statistics", methods=['GET'])
def get_latest_statistics_endpoint():
    """
    Retrieve latest statistics either from cache or by generating new
    """
    cached_data = get_cached_data()
    if cached_data:
        return jsonify(cached_data)

    dates = Statistic.get_dates()
    info = get_stats(dates[0])

    # Convert class objects to dictionaries
    cached_data = dict(
        stats=[vars(_) for _ in info[1]],
        positions=[vars(_) for _ in info[2]],
        ways=[vars(_) for _ in info[3]]
    )
    set_cached_data(cached_data)

    return jsonify(cached_data)


@app.route("/get_language_comparison", methods=['GET'])
def get_language_comparison_endpoint():
    """
    Generate or retrieve language comparison image
    """
    if not os.path.isfile('./static/images/languages.png'):
        get_languages_comparison()

    # Add timestamp to prevent caching
    rand = str(datetime.now()).replace(' ', '_')
    return jsonify({
        'image': os.path.abspath(f'./static/images/languages.png?v={rand}')
    })


@app.route("/statistic/<date>")
def show_specific_statistics(date: datetime):
    """
    Show statistics for a specific date
    """
    dates = Statistic.get_str_dates()
    try:
        info = get_stats(date)
        return render_template('statistics.html',
            links=info[0],
            stats=info[1],
            positions=info[2],
            ways=info[3],
            tech=info[4],
            dates=dates
        )
    except IndexError:
        return render_template('error.html', tech=[{'date_collected': date}])


# SKILLS
@app.route("/skill")
def show_stats_by_skill():
    clear_graph()
    info = get_skill_stats(10)
    return render_template('skill.html',
        skills=info[1],
        stats=info[0],
        selected_skill=info[2]
    )


@app.route("/skill/<skill_id>")
def show_stats_by_specific_skill(skill_id: str):
    """
    Show statistics for a specific skill
    """
    if not skill_id.isnumeric():
        abort(400, f'Unknown skill_id - "{skill_id}"')

    info = get_skill_stats(int(skill_id))
    return render_template('skill.html',
        skills=info[1],
        stats=info[0],
        selected_skill=info[2]
    )


@app.route("/clear_graph")
def clear_graph():
    """
    Clear existing graph image
    """
    if os.path.exists('static/images/graph.png'):
        os.remove('static/images/graph.png')
    clear_plt()

    link = redirect_url()
    if link:
        return redirect(link)
    else:
        return redirect(url_for('show_stats_by_skill'))


def redirect_url(default='index'):
    """
    Get the redirect URL from request arguments
    """
    return request.args.get('next') or request.referrer


# VACANCIES
@app.route('/get_vac', methods=['POST'])
def get_vac():
    """
    Redirect to vacancies for a specific skill
    """
    skill_id = request.form['skill_id']
    date = request.form['date']
    return redirect(f'/skill_vacancies/{skill_id}_{date}')


@app.route("/skill_vacancies/<skill_id>_<date>")
def show_vacancies_by_specific_skill(skill_id, date):
    """
    Show vacancies for a specific skill and date
    """
    dates = Statistic.get_str_dates()
    skills = get_skill_list()
    selected = [_ for _ in skills if _['id'] == int(skill_id)][0]
    vacancies = get_vacancies_by_skill(date, selected['name'])['vacancies']
    return render_template('skill_vacancies.html',
        skills=skills,
        vacancies=vacancies,
        selected_skill=[selected],
        dates=dates,
        tech=[{'date_collected': date}]
    )


@app.route("/skill_vacancies")
def show_vacancies_by_skill():
    """
    Show vacancies for the default skill
    """
    dates = Statistic.get_str_dates()
    skills = get_skill_list()
    selected = [_['id'] for _ in skills if _['id'] == 10][0]
    vacancies = get_vacancies_by_skill(dates[0], selected['name'])['vacancies']
    return render_template('skill_vacancies.html',
        skills=skills,
        vacancies=vacancies,
        selected_skill=[selected],
        dates=dates,
        tech=[{'date_collected': dates[0]}]
    )


# ERRORS
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', title='404'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('500.html', title='500'), 500


@app.errorhandler(400)
def client_error(error):
    error_msg = str(error).replace('400 Bad Request: ', '')
    return render_template('400.html', title='400', error_msg=error_msg), 400


def create_app():
    return app


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7100, debug=True)