from Instastories import start_scrape, login_and_store_session_id
from flask import Flask, render_template, request, redirect
import os
import base64
import shutil
import settings
import logging

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

SKIP_EXTENSIONS = (".json", ".txt")

settings.setup_logger()
logger = logging.getLogger(__name__)

################### UTIL FUNCTIONS ###################

def get_log_file_list():
    with open(settings.get('scraping_log_file_path'), "r+") as o:
        return [log_lines for log_lines in o.readlines()]

def convert_media_files(base64_media):
    converted_files = []
    last_username = None
    for base64_data, media_type, username in base64_media:
        content_tag = "img" if media_type == "img/png" else "video controls"
        if username != last_username:
            converted_files.append({"type": "username", "data": username})
            last_username = username
        converted_files.append({"type": "media",
                                "data": {"content_tag": content_tag,
                                         "media_type": media_type,
                                         "base64_data": base64_data}
                                })
    return converted_files

def get_folders(path, url):
    rendered_folders = []  # List of {type: 'folder', url: X, name: Y}
    if not os.path.exists(path): return []
    for folder in os.listdir(path):
        if folder.endswith(SKIP_EXTENSIONS): continue
        rendered_folders.append({'type': 'folder',
                                 'url': f"{url}{folder}",
                                 'name': f"{folder}"})
    return rendered_folders

def get_media(path):
    to_render_media = []
    for media in os.listdir(path):
        if media.endswith(SKIP_EXTENSIONS): continue
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

@app.route("/", methods=['GET', 'POST'])
def index():
    converted_files = []
    is_user_logged_in = settings.has_setting("session_id")
    folder_path = settings.get("folder_path")
    if request.method == "POST" and is_user_logged_in:
        amount_to_scrape = int(request.form["amountToScrape"]) if request.form["amountToScrape"].isdecimal() else -1
        mode, ids_mode = request.form["mode_dropdown"], request.form["ids_dropdown"]
        logger.info(f"Starting scraping in mode: {mode}, ids source: {ids_mode}")
        base64_media = start_scrape(settings.get(), folder_path, amount_to_scrape, mode, ids_mode)
        logger.info("Finished scraping")
        converted_files = convert_media_files(base64_media)
    logged_in_error = request.method == "POST" and not is_user_logged_in
    log_lines = get_log_file_list()
    logger.info("Loading index")
    return render_template('index.html', log_lines=log_lines, images=converted_files, disclaimer={"logged_in_error": logged_in_error})

@app.route("/settings/", methods=['GET', 'POST'])
def settings_page():
    if not settings.has_setting("session_id"):
        return redirect("/login")  # Prompt the user to log-in if he's not
        logger.info("User not logged in, redirected to /login")
    if request.method == "POST":  # User is updating settings.
        for setting_name in request.form:
            if setting_name == "extra_ids":
                extra_ids = request.form["extra_ids"].splitlines()
                settings.update("extra_ids", extra_ids)
            elif len(request.form[setting_name]) != 0:  # Updates other non-null settings.
                settings.update(setting_name, request.form[setting_name])
        logger.info("Updated settings")
    folder_path = settings.get("folder_path")
    extra_ids = settings.get("extra_ids")
    return render_template("settings.html", folder_path=folder_path, extra_ids=extra_ids)

@app.route("/login", methods=['GET', 'POST'])
def login_page():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        if login_and_store_session_id(request.form["username"], request.form["password"]):
            logger.info("User {} has logged in".format(request.form["username"]))
            return redirect("/settings")
        else:
            return render_template("login.html", disclaimer={"login_error": True})

@app.route("/settings/logout")
def logout():
    settings.clear_setting("session_id")
    logger.info("The user has logged out")
    return render_template("login.html", disclaimer={"login_error": False})

@app.route("/settings/delete-media")
def delete_media_folder_if_present():
    folder_path = settings.get("folder_path")
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        logger.info(f"Deleted {folder_path} folder")

@app.route("/gallery/", methods=['GET'], defaults={"username": None, "date": None})
@app.route("/gallery/<username>/", methods=['GET'], defaults={"date": None})
@app.route("/gallery/<username>/<date>/", methods=['GET'])
def gallery(username, date):
    folder_path = settings.get("folder_path")
    # From most to least specific
    if date:
        date_path = os.path.join(os.path.join(folder_path, username), date)
        to_render_items = get_media(date_path)
    elif username:
        user_path = os.path.join(folder_path, username)
        to_render_items = get_folders(user_path, request.url)
    else:
        to_render_items = get_folders(folder_path, request.url)
    return render_template("gallery.html", to_render_items=to_render_items)

################### RUN ###################


if __name__ == "__main__":
    app.run()
