from Instastories import scrape_from_web
from flask import Flask, render_template, request
import os
app = Flask(__name__)

COOKIE_PATH = "token.txt"

def setLogFileList():
    rendered_log = []
    if not os.path.exists("run_history.log"):
        f = open("run_history.log", "w").close()

    with open("run_history.log", "r") as o:
        for i in o.readlines():
            rendered_log.append(str(i))
        return rendered_log


@app.route("/")
def index():
    render_log = setLogFileList()
    return render_template("index.html", count_i = 0, count_v = 0, rendered_log = render_log)

	
@app.route("/scrape/", methods=['POST'])

def scrape():
    if request.method == "POST":
        amountScraped = int(request.form["amountToScrape"])
        count_i, count_v = scrape_from_web(COOKIE_PATH, amountScraped)

        rendered_log = setLogFileList()
        return render_template('index.html', count_i = count_i, count_v = count_v, rendered_log = rendered_log)


	



if __name__ == "__main__":
    app.run()