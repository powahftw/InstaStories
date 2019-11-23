from Instastories import scrape_from_web
from flask import Flask, render_template, request, url_for, flash
import os
import json

app = Flask(__name__)

################### UTIL FUNCTIONS ###################

def setLogFileList():
    log_line = []

    if not os.path.exists("run_history.log"):
        open("run_history.log", "w").close()

    with open("run_history.log", "r") as o:
        return [log_line for log_line in o.readlines()]


def saveSettings(settings):
    with open("settings.json", "w+") as settings_json:
        json.dump(settings, settings_json)

def getSettings():
    if os.path.exists("settings.json"):
        with open("settings.json", "r") as settings_json:
            settings = json.load(settings_json)
        return settings
    else: return {}


################### ROUTES ###################

@app.route("/", methods=['GET','POST'])
def index():
    log_line = setLogFileList()

    settings = getSettings()    # Gets the settings
    cookie_path = settings["cookie_path"] if "cookie_path" in settings else "token.txt"
    folder_path = settings["folder_path"]  if "folder_path" in settings else "ig_media"

    if request.method == "POST":
        amountScraped = int(request.form["amountToScrape"])
        mode = request.form["mode_dropdown"]
        count_i, count_v, base64_images = scrape_from_web(cookie_path, folder_path, amountScraped, mode)

        log_line = setLogFileList()
        return render_template('index.html', count_i = count_i, count_v = count_v, log_line = log_line, images = base64_images)
    else:
        return render_template("index.html", count_i = 0, count_v = 0, log_line = log_line)

	
@app.route("/settings/", methods=['GET','POST'])
def settings():

    settings = getSettings()    # Gets the settings
    cookie_path = settings["cookie_path"] if "cookie_path" in settings else "token.txt"
    folder_path = settings["folder_path"]  if "folder_path" in settings else "ig_media"

    if request.method == "POST":
        updated_settings = {}

        for setting in request.form:
            if len(request.form[setting]) > 0:
                updated_settings[setting] = request.form[setting]
        saveSettings(updated_settings)


        return render_template("settings.html", folder_path = updated_settings["folder_path"] if "folder_path" in updated_settings else folder_path, cookie_path = updated_settings["cookie_path"] if "cookie_path" in updated_settings else cookie_path)
    else:
        return render_template("settings.html", folder_path = folder_path, cookie_path = cookie_path)

################### RUN ###################
if __name__ == "__main__":
    app.run()