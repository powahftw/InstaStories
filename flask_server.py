from Instastories import scrape_from_web
from flask import Flask, render_template, request, url_for, flash
import os
import json
app = Flask(__name__)

################### UTIL FUNCTIONS ####################

def setLogFileList():
    log_line = []

    if not os.path.exists("run_history.log"):
        open("run_history.log", "w").close()

    with open("run_history.log", "r") as o:
        return [log_line for log_line in o.readlines()]

def savePaths(cookie_path, folder_path):
    paths_dict = {'cookie_path' : cookie_path, 'folder_path' : folder_path}
    with open('paths.json', 'w') as f:
        json.dump(paths_dict, f)

def setUpdatedPaths():
    with open('paths.json', 'r') as f:
        paths_dict = json.load(f)

    # Returns cookie_path, folder_path

    return paths_dict["cookie_path"], paths_dict["folder_path"]

################### ROUTES #################

@app.route("/", methods=['GET','POST'])
def index():
    log_line = setLogFileList()

    if request.method == "POST":
        amountScraped = int(request.form["amountToScrape"])
        count_i, count_v = scrape_from_web(cookie_path, folder_path, amountScraped)
        log_line = setLogFileList()
        return render_template('index.html', count_i = count_i, count_v = count_v, log_line = log_line, error = "0")

    return render_template("index.html", count_i = 0, count_v = 0, log_line = log_line)

	
@app.route("/settings/", methods=['GET','POST'])
def settings():
    global cookie_path, folder_path

    if request.method == "POST":
        if len(request.form["cookie_path"]) > 0:
            new_cookie_path = request.form["cookie_path"]
        else:
            new_cookie_path = os.path.join(os.getcwd(), cookie_path)

        if len(request.form["folder_name"]) > 0:
            new_folder_path = request.form["folder_name"]
        else:
            new_folder_path = os.path.join(os.getcwd(), folder_path)

        savePaths(new_cookie_path, new_folder_path)
        cookie_path, folder_path = setUpdatedPaths()
        return render_template("settings.html", folder_path = os.path.join(os.getcwd(), folder_path), cookie_path = os.path.join(os.getcwd(), cookie_path))

    return render_template("settings.html", folder_path = os.path.join(os.getcwd(), folder_path), cookie_path = os.path.join(os.getcwd(), cookie_path))

############### RUN #####################

if __name__ == "__main__":

    if os.path.exists("paths.json"):
        cookie_path, folder_path = setUpdatedPaths()
    else:
        cookie_path = "token.txt"
        folder_path = "ig_media"

    app.run()