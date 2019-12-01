from Instastories import start_scrape
from flask import Flask, render_template, request, url_for, Markup
import os
import json

app = Flask(__name__)

################### UTIL FUNCTIONS ###################

def set_log_file_list():
    log_line = []
    if not os.path.exists("run_history.log"):
        open("run_history.log", "w").close()
    with open("run_history.log", "r") as o:
        return [log_line for log_line in o.readlines()]


def save_settings(settings):
    with open("settings.json", "w+") as settings_json:
        json.dump(settings, settings_json)

def get_settings():
    if not os.path.exists("settings.json"):
        return {}
    with open("settings.json", "r") as settings_json:
        return json.load(settings_json)

def render_base64_media(base64_media):
    rendered_base64_media = []
    index_username = None
    for media in base64_media:
        base64_data, media_type, username = media
        content_tag = "img" if "img" in media_type else "video controls"
        if username != index_username:
            rendered_base64_media.append(Markup(f"<hr><div class=\"username-text\">{username}</div><br>"))
            rendered_base64_media.append(Markup(f"<{content_tag} src=\"data:{media_type};base64,{base64_data}\" class=\"rendered-stories\"></{content_tag}>"))
            index_username = username
        else:
            rendered_base64_media.append(Markup(f"<{content_tag} src=\"data:{media_type};base64,{base64_data}\" class=\"rendered-stories\"></{content_tag}>"))
    return rendered_base64_media
        


################### ROUTES ###################

@app.route("/", methods=['GET','POST'])
def index():
    log_line = set_log_file_list()
    settings = get_settings()
    count_i, count_v = 0, 0
    rendered_base64_media = []
    cookie_path = settings["cookie_path"] if "cookie_path" in settings else "token.txt"
    folder_path = settings["folder_path"]  if "folder_path" in settings else "ig_media"

    if request.method == "POST":
        amountScraped = int(request.form["amountToScrape"])
        mode = request.form["mode_dropdown"]
        count_i, count_v, base64_media = start_scrape(cookie_path, folder_path, amountScraped, mode)
        rendered_base64_media = render_base64_media(base64_media)
        log_line = set_log_file_list()
    return render_template('index.html', count_i = count_i, count_v = count_v, log_line = log_line, images = rendered_base64_media)

	
@app.route("/settings/", methods=['GET','POST'])
def settings():

    settings = get_settings()    # Gets the settings
    cookie_path = settings["cookie_path"] if "cookie_path" in settings else "token.txt"
    folder_path = settings["folder_path"]  if "folder_path" in settings else "ig_media"
    updated_settings = {}

    if request.method == "POST":
        for setting in request.form:
            if len(request.form[setting]) > 0:
                updated_settings[setting] = request.form[setting]
        save_settings(updated_settings)
    return render_template("settings.html", folder_path = updated_settings["folder_path"] if "folder_path" in updated_settings else folder_path, cookie_path = updated_settings["cookie_path"] if "cookie_path" in updated_settings else cookie_path)

@app.route("/gallery/", methods=['GET'])
def gallery():
    settings = get_settings()    # Gets the settings
    folder_path = settings["folder_path"]  if "folder_path" in settings else "ig_media"
    


    return render_template("gallery.html")




################### RUN ###################
if __name__ == "__main__":
    app.run()