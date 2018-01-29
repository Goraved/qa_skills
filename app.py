from flask import Flask, render_template

from parse import *

app = Flask(__name__)


@app.route("/")
def main():
    return render_template('index.html')


@app.route("/get_statistics")
def get_actual_statistics():
    get_statistics()
    return render_template('statistics.html')


@app.route("/statistics")
def show_statistics():
    return render_template('statistics.html')


if __name__ == "__main__":
    app.run()
