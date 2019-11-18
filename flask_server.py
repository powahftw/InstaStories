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


def saveSettings(settings_dict):
    with open("settings.json", "w+") as settings_json:
        json.dump(settings_dict, settings_json)

def getSettings():

    if not os.path.exists("settings.json"):
        settings_dict = {"cookie_path": "token.txt", "folder_path": "ig_media"}
    else:
        with open("settings.json") as settings_json:
            settings_dict = json.load(settings_json)

    return settings_dict

################### ROUTES #################

@app.route("/", methods=['GET','POST'])
def index():
    log_line = setLogFileList()

    if request.method == "POST":
        amountScraped = int(request.form["amountToScrape"])
        mode = request.form["mode_dropdown"]
        count_i, count_v = scrape_from_web(getSettings()["cookie_path"], getSettings()["folder_path"], amountScraped, mode)
        log_line = setLogFileList()
        return render_template('index.html', count_i = count_i, count_v = count_v, log_line = log_line)
    else:
        return render_template("index.html", count_i = 0, count_v = 0, log_line = log_line)

	
@app.route("/settings/", methods=['GET','POST'])
def settings():
    if request.method == "POST":

        # Dictionary of default settings values
        # Creates the new dictionary for updated settings
        new_settings_dict = {"cookie_path": "token.txt", "folder_path": "ig_media"}

        for setting in request.form:
            if len(request.form[setting]) > 0:
                new_settings_dict[setting] = request.form[setting]
            elif os.path.exists("settings.json"):
                with open("settings.json") as settings_json:
                    settings_json_dict = json.load(settings_json)
                    new_settings_dict[setting] = settings_json_dict[setting]

        saveSettings(new_settings_dict)

        return render_template("settings.html", folder_path = getSettings()["folder_path"], cookie_path = getSettings()["cookie_path"])
    else:
        return render_template("settings.html", folder_path = getSettings()["folder_path"], cookie_path = getSettings()["cookie_path"])

############### RUN #####################

if __name__ == "__main__":
    app.run()