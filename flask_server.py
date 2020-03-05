from Instastories import start_scrape, get_session_id
from flask import Flask, render_template, request, url_for, Markup
import os, json, base64, time, random, re

app = Flask(__name__)

################### UTIL FUNCTIONS ###################

def get_log_file_list():
    if not os.path.exists("run_history.log"):
        open("run_history.log", "w").close()
    with open("run_history.log", "r") as o:
        return [log_lines for log_lines in o.readlines()]

def save_settings(settings):
    with open("settings.json", "w+") as settings_json:
        json.dump(settings, settings_json)

def get_settings():
    if not os.path.exists("settings.json"):
        return {}
    with open("settings.json", "r") as settings_json:
        return json.load(settings_json)

def create_markup(base64_data, media_type = None, username = None):
    if username != None:
        return Markup((f"<hr><div class=\"username-text\">{username}</div><br>"))
    if media_type in ["video/mp4", "img/png"]:
        content_tag = "img" if media_type == "img/png" else "video controls"
        return Markup(f"<{content_tag} src=\"data:{media_type};base64,{base64_data}\" class=\"rendered-stories\"></{content_tag}>")

def render_base64_media(base64_media):
    rendered_base64_media = []
    last_username = None
    for base64_data, media_type, username in base64_media:
        if username != last_username:
            rendered_base64_media.append(create_markup(base64_data, username = username))
            last_username = username
        rendered_base64_media.append(create_markup(base64_data, media_type))
    return rendered_base64_media

def get_rendered_folders(path, url):
    rendered_folders = []
    if not os.path.exists(path) : return []
    for folder in os.listdir(path):
        rendered_folders.append(Markup(f"<a href=\"{url}{folder}\" class=\"urls\">{folder}</a>"))
    return rendered_folders

def get_rendered_media(path):
    rendered_media = []
    for media in os.listdir(path):
        if media.endswith(".json"): continue
        media_type = "img/png" if media.endswith(".jpg") else "video/mp4"
        with open(f"{path}\\{media}", "rb") as media_element:
            base64_media = base64.b64encode(media_element.read()).decode("utf-8")
        rendered_media.append(create_markup(base64_media, media_type))
    return rendered_media

def get_stats_from_log_line(log_lines):
    _, users_count, img_count, video_count = log_lines[-1].split(" - ")
    count_u, count_i, count_v = [int(val.strip().split(" ")[0]) for val in [users_count, img_count, video_count]]
    return count_u, count_i, count_v
   
################### ROUTES ###################

@app.route("/", methods=['GET','POST'])
def index():
    settings = get_settings()
    count_i, count_v, count_u = 0, 0, 0
    rendered_base64_media = []
    cookie_path = settings["cookie_path"] if "cookie_path" in settings else "token.txt"
    folder_path = settings["folder_path"]  if "folder_path" in settings else "ig_media"
    if request.method == "POST":
        if not os.path.exists("token.txt"):
            log_lines = get_log_file_list() 
            return render_template('index.html', count_i= count_i, count_v = count_v, log_lines = log_lines, images = rendered_base64_media, empty_form = False, logged_in = False)
        if request.form["amountToScrape"].isnumeric():
            amountScraped = int(request.form["amountToScrape"])
        else:
            log_lines = get_log_file_list() 
            return render_template('index.html', count_i= count_i, count_v = count_v, log_lines = log_lines, images = rendered_base64_media, empty_form = True, logged_in = True)
        mode = request.form["mode_dropdown"]
        base64_media = start_scrape(cookie_path, folder_path, amountScraped, mode)
        rendered_base64_media = render_base64_media(base64_media)
    log_lines = get_log_file_list()   
    if len(log_lines) > 0:
        count_u, count_i, count_v = get_stats_from_log_line(log_lines)      
    return render_template('index.html', count_i = count_i, count_v = count_v, log_lines = log_lines, images = rendered_base64_media, empty_form = False, logged_in = True)

@app.route("/settings/", methods=['GET','POST'])
def settings():
    credentials_error = False
    settings = get_settings()    # Gets the settings
    if request.method == "POST":
        updated_settings = settings
        for setting in request.form:
            if len(request.form[setting]) > 0:
                updated_settings[setting] = request.form[setting]
        save_settings(updated_settings)
        if request.form["username"] and request.form["password"] != "":
            if not get_session_id(request.form["username"], request.form["password"]) == 0:
                credentials_error = True
    cookie_path = settings["cookie_path"] if "cookie_path" in settings else "token.txt"
    folder_path = settings["folder_path"]  if "folder_path" in settings else "ig_media"
    if os.path.exists("token.txt"):
        logged_in = True
    else:
        logged_in = False
    return render_template("settings.html", folder_path = folder_path, cookie_path = cookie_path, logged_in = logged_in, credentials_error = credentials_error)

@app.route("/gallery/", methods=['GET'], defaults = {"username": None, "date": None})
@app.route("/gallery/<username>/", methods=['GET'], defaults = {"date": None})
@app.route("/gallery/<username>/<date>/", methods=['GET'])
def gallery(username, date):
    settings = get_settings()
    folder_path = settings["folder_path"]  if "folder_path" in settings else "ig_media" 
    if date != None:
        date_path = os.path.join(os.path.join(folder_path, username), date)
        rendered_items = get_rendered_media(date_path)
    elif username != None:
        user_path = os.path.join(folder_path, username)
        rendered_items = get_rendered_folders(user_path, request.url)
    else:
        rendered_items = get_rendered_folders(folder_path, request.url)
     
    return render_template("gallery.html", rendered_items = rendered_items )

################### RUN ###################
if __name__ == "__main__":
    app.run()
    