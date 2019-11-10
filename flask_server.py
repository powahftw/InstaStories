from Instastories import scrape_from_web
from flask import Flask, render_template, request
import os
app = Flask(__name__)

COOKIE_PATH = "token.txt"

def setLogFileList():
    log_line = []

    if not os.path.exists("run_history.log"):
        open("run_history.log", "w").close()

    with open("run_history.log", "r") as o:
        return [log_line for log_line in o.readlines()]


@app.route("/")
def index():
    log_line = setLogFileList()
    return render_template("index.html", count_i = 0, count_v = 0, log_line = log_line)

	
@app.route("/scrape/", methods=['POST'])

def scrape():
    if request.method == "POST":
        amountScraped = int(request.form["amountToScrape"])
        count_i, count_v = scrape_from_web(COOKIE_PATH, amountScraped)

        log_line = setLogFileList()
        return render_template('index.html', count_i = count_i, count_v = count_v, log_line = log_line)


	



if __name__ == "__main__":
    app.run()