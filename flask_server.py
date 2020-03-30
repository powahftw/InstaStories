from Instastories import start_scrape, store_session_id, get_settings, save_settings
from flask import Flask, render_template, request, url_for, Markup, redirect
import os, json, base64, time, random, shutil

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

################### UTIL FUNCTIONS ###################

def check_login_status():
    settings = get_settings()
    return True if "session_id" in settings else False

def get_log_file_list():
    if not os.path.exists("run_history.log"):
        open("run_history.log", "w").close()
    with open("run_history.log", "r") as o:
        return [log_lines for log_lines in o.readlines()]

def create_markup(base64_data, media_type = None, username = None):
    if username != None:
        return Markup((f"<hr><div class=\"username-text\">{username}</div><br>"))
        
def convert_media_files(base64_media):
    converted_files = []                      # converted_files struct:  {"type": username, "data": base64_data or username}          base64data = {"content_tag", "media_type", "data"}
    last_username = None
    for base64_data, media_type, username in base64_media:
        content_tag = "img" if media_type == "img/png" else "video controls"
        if username != last_username:
            converted_files.append({"type": "username", "data": username})
            last_username = username
        converted_files.append({"type": "media", "data": {"content_tag": content_tag,"media_type": media_type,"base64_data": base64_data}})     
    return converted_files

def get_folders(path, url):
    rendered_folders = [] # List of {url: X, name: Y}
    if not os.path.exists(path) : return []
    for folder in os.listdir(path):
        rendered_folders.append({'type': 'folder', 'url': f"{url}{folder}", 'name': f"{folder}"})
    return rendered_folders

def get_media(path):
    to_render_media = []
    for media in os.listdir(path):
        if media.endswith(".json"): continue
        media_type = "img/png" if media.endswith(".jpg") else "video/mp4"
        content_tag = "img" if media_type == "img/png" else "video controls"
        with open(os.path.join(path, media), "rb") as media_element:
            base64_media = base64.b64encode(media_element.read()).decode("utf-8")
        to_render_media.append({'type': 'media', 'content_tag': content_tag, 'media_type': media_type, 'data': base64_media})
    return to_render_media

def get_stats_from_log_line(log_lines):
    _, users_count, img_count, video_count = log_lines[-1].split(" - ")
    count_u, count_i, count_v = [int(val.strip().split(" ")[0]) for val in [users_count, img_count, video_count]]
    return count_u, count_i, count_v
   
################### ROUTES ###################

@app.route("/", methods=['GET','POST'])
def index():
    converted_files = []
    settings = get_settings()
    folder_path = settings["folder_path"] if "folder_path" in settings else "ig_media"
    if request.method == "POST" and check_login_status():
        amount_to_scrape = int(request.form["amountToScrape"]) if request.form["amountToScrape"].isnumeric() else -1
        mode = request.form["mode_dropdown"]
        ids_mode = request.form["ids_dropdown"]
        base64_media = start_scrape(settings, folder_path, amount_to_scrape, mode, ids_mode)
        converted_files = convert_media_files(base64_media)
    logged_in_error = request.method == "POST" and not check_login_status()  
    log_lines = get_log_file_list()
    return render_template('index.html', log_lines = log_lines, images = converted_files, disclaimer = {"logged_in_error": logged_in_error})

@app.route("/settings/", methods=['GET','POST'])
def settings():
    settings = get_settings()    # Gets the settings
    if not "session_id" in settings: return redirect("/login")  # Prompt the user to log-in if he's not
    folder_path = settings["folder_path"] if "folder_path" in settings else "ig_media"
    extra_ids = settings["extra_ids"] if "extra_ids" in settings else []
    if request.method == "POST":
        updated_settings = settings
        for setting in request.form:
            if len(request.form[setting]) > 0:
                if setting == "extra_ids":
                    updated_settings[setting] = list(map(int, request.form[setting].splitlines()))
                    continue
                updated_settings[setting] = request.form[setting]    
        save_settings(updated_settings)
        extra_ids = updated_settings["extra_ids"]
    return render_template("settings.html", folder_path = folder_path, extra_ids = extra_ids)

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
            if store_session_id(request.form["username"], request.form["password"]):
                return redirect("/settings")
            else: 
                return render_template("login.html", disclaimer = {"login_error": True})
    
@app.route("/settings/logout")
def logout():
    settings = get_settings()
    settings.pop("session_id", None)
    save_settings(settings)
    return render_template("login.html", disclaimer = {"login_error": False})

@app.route("/settings/delete-media")
def delete_media():
    settings = get_settings()
    folder_path = settings["folder_path"] if "folder_path" in settings else "ig_media"
    shutil.rmtree(folder_path)

@app.route("/gallery/", methods=['GET'], defaults = {"username": None, "date": None})
@app.route("/gallery/<username>/", methods=['GET'], defaults = {"date": None})
@app.route("/gallery/<username>/<date>/", methods=['GET'])
def gallery(username, date):
    settings = get_settings()
    folder_path = settings["folder_path"] if "folder_path" in settings else "ig_media"
    if date != None:
        date_path = os.path.join(os.path.join(folder_path, username), date)
        to_render_items = get_media(date_path)
    elif username != None:
        user_path = os.path.join(folder_path, username)
        to_render_items = get_folders(user_path, request.url)
    else:
        to_render_items = get_folders(folder_path, request.url)
     
    return render_template("gallery.html", to_render_items = to_render_items )

################### RUN ###################
if __name__ == "__main__":
    app.run()
    