from Instastories import start_scrape
from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import shutil
import settings
import logging
from thread_runner import ThreadRunner

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

SKIP_EXTENSIONS = (".json", ".txt")
PAGINATE_EVERY_N_ROWS = 100

settings.setup_logger()
logger = logging.getLogger(__name__)
user_settings = settings.get()

scraper_runner = ThreadRunner(start_scrape, user_settings["loop_delay_seconds"], user_settings["loop_variation_percentage"])

################### UTIL FUNCTIONS ###################

def get_log_file_list():
    scraping_logs_path = settings.get('scraping_log_file_path')
    if not os.path.exists(scraping_logs_path):
        return []
    with open(scraping_logs_path, "r+") as o:
        logs = [log_lines for log_lines in o.readlines()]
        return logs[::-1]

def get_folders(path, ids_to_names={}):
    rendered_folders = []  # List of {type: 'folder', name: Y}
    if not os.path.exists(path): return []
    for folder in os.listdir(path):
        if folder.endswith(SKIP_EXTENSIONS): continue

        # In the user names page we convert the ids to more usable displayed name.
        displayed_name = ids_to_names.get(folder, folder)

        rendered_folders.append({'type': 'folder',
                                 'name': f'{displayed_name}',
                                 'id': f'{folder}'})
    return rendered_folders

def get_media_files(path):
    to_render_media = []
    for media in os.listdir(path):
        if media.endswith(SKIP_EXTENSIONS): continue
        to_render_media.append({'type': 'media', 'name': media, 'is_img': media.endswith(".jpg")})
    return to_render_media

def get_stats_from_log_line(log_lines):
    _, users_count, img_count, video_count = log_lines[-1].split(" - ")
    count_u, count_i, count_v = [int(val.strip().split(" ")[0]) for val in [users_count, img_count, video_count]]
    return count_u, count_i, count_v

def get_disk_usage():
    hdd_usage = shutil.disk_usage("/")
    total_disk_size, used_disk_size, free_disk_size = map(lambda bytes: bytes // (2**30), hdd_usage)
    return {
        "used_space": used_disk_size,
        "free_space": free_disk_size,
        "total_space": total_disk_size,
    }

def get_app_logs():
    log_file_path = settings.get('system_log_file_path')
    if not os.path.exists(log_file_path): return []
    with open(log_file_path, 'r+') as log_file:
        return [log for log in log_file.readlines()[::-1]]

def get_scraper_status():
    return {
        "log_lines": get_log_file_list(),
        "logged_in": "session_id" in user_settings,
        "output": scraper_runner.getOutput(),
        "status": scraper_runner.getStatus()
    }

def get_scraper_settings():
    args = scraper_runner.args
    loop_mode = len(args) != 0 and not scraper_runner.shutting_down
    media_mode = scraper_runner.args['media_mode'] if args else "all"
    ids_source = scraper_runner.args['ids_source'] if args else "all"
    return {
        "loop_mode": loop_mode,
        "media_mode": media_mode,
        "ids_source": ids_source
    }

################### ROUTES ###################

@app.route("/")
def index():
    logger.info(f"{request.method} request to /index")
    return render_template('index.html')

@app.route("/settings/", methods=['GET', 'POST'])
def settings_page():
    logger.info(f"{request.method} request to /settings/")
    return render_template("settings.html")

@app.route("/gallery/", methods=['GET'], defaults={"text": ''})
@app.route("/gallery/<path:text>", methods=['GET'])
def gallery(text):
    logger.info(f"GET request to /gallery/")
    return render_template("gallery.html")


@app.route("/logs/", methods=['GET'])
def logs():
    return render_template('logs.html')

################### API ROUTES ###################

@app.route("/api/scraper/status/", methods=["GET", "POST"])
def running_status():
    logger.info(f"API/{request.method} request to /scraper/status")

    if request.method == "POST":
        res = request.get_json()
        user_settings = settings.get()
        if "session_id" not in user_settings:
            return {"status": "not logged in"}

        if res['command'] == "start":
            scraping_args = res['scraping_args']
            loop_mode = res['loop_mode'] == 'true'
            scraper_runner.updateFuncArg(**scraping_args).startFunction(keep_running=loop_mode)
        else:
            scraper_runner.stopFunction()

    return jsonify(get_scraper_status())

@app.route("/api/scraper/settings/", methods=["GET"])
def scraper_settings():
    logger.info(f"API/{request.method} request to /scraper/settings/")
    return jsonify(get_scraper_settings())

class PageType:
    USERS_VIEW = 1
    DATES_VIEW = 2
    MEDIA_VIEW = 3

@app.route("/api/gallery/", methods=['GET'], defaults={"user_id": None, "date": None})
@app.route("/api/gallery/<user_id>/", methods=['GET'], defaults={"date": None})
@app.route("/api/gallery/<user_id>/<date>/", methods=['GET'])
def gallery_api(user_id, date):
    logger.info(f"API/{request.method} request to /gallery/{user_id if user_id else ''}{'/' + date if date else ''}")
    folder_path = settings.get("media_folder_path")

    # From most to least specific
    if date:
        view = PageType.MEDIA_VIEW
    elif user_id:
        view = PageType.DATES_VIEW
    else:
        view = PageType.USERS_VIEW

    ids_to_names = settings.get_ids_to_names_file()
    page_title = 'Gallery'
    if user_id:
        page_title += f"/{ids_to_names.get(user_id, user_id)}"
        if date:
            page_title += f"/{date}"

    if view == PageType.MEDIA_VIEW:
        date_path = os.path.join(os.path.join(folder_path, user_id), date)
        to_render_items = get_media_files(date_path)
    elif view == PageType.DATES_VIEW:
        user_path = os.path.join(folder_path, user_id)
        to_render_items = get_folders(user_path, ids_to_names=ids_to_names)
    else:
        to_render_items = get_folders(folder_path, ids_to_names=ids_to_names)
    return jsonify({'title': page_title, 'items': to_render_items})

@app.route("/api/gallery/", methods=['DELETE'])
def delete_media():
    folder_path = settings.get("media_folder_path")
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        logger.info(f"Deleted {folder_path} folder")
    return jsonify(success=True)

@app.route("/api/settings/", methods=['GET', 'POST'])
def get_settings_api():
    logger.info(f"API/{request.method} request to /settings/")
    if request.method == 'GET':
        return jsonify(settings.get())
    elif request.method == 'POST':
        user_settings = settings.get()
        res = request.get_json()
        user_settings.update(res)
        settings.update_settings_file(user_settings)

        loop_args = {"loop_delay_seconds": int(user_settings["loop_delay_seconds"]),
                     "loop_variation_percentage": int(user_settings["loop_variation_percentage"])}
        scraper_runner.updateDelay(**loop_args)
        return jsonify(user_settings)

@app.route('/api/settings/logout/', methods=["GET"])
def logout():
    logger.info(f"API/{request.method} request to /settings/logout/")
    settings.clear_setting("session_id")
    logger.info("The user has logged out")
    return jsonify(success=True)

@app.route('/api/settings/diskusage')
def disk_usage():
    return jsonify(get_disk_usage())

@app.route("/api/logs/<int:page>/", methods=['GET'])
def get_logs(page):
    logs = get_app_logs()
    paginated_logs = [logs[start:start+PAGINATE_EVERY_N_ROWS] for start in range(0, len(logs), PAGINATE_EVERY_N_ROWS)]
    if page < 1 or page > len(paginated_logs):
        return jsonify({"page": -1, "max_page": len(paginated_logs), "logs": []})
    return jsonify({"page": page, "max_page": len(paginated_logs), "logs": paginated_logs[page - 1]})

################### SERVE MEDIA ###################

@app.route("/gallery/<username>/<date>/<filename>", methods=['GET'])
def serve_media(username, date, filename):
    folder_path = settings.get("media_folder_path")
    media_folder = os.path.join(os.path.join(folder_path, username), date)
    return send_from_directory(media_folder, filename)

################### RUN ###################


if __name__ == "__main__":
    app.run(debug=True, port=80, host='0.0.0.0')
