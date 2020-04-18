import requests
import json
import urllib.request
import os
import time
import datetime
import settings
import logging
from random import randint

try:
    from terminaltables import AsciiTable
    PRINT_TABLE = True
except ImportError as e:
    PRINT_TABLE = False

logger = logging.getLogger(__name__)

################# UTILS FUNCTIONS #########################

def login_and_store_session_id(username, password):
    LOGIN_URL = 'https://www.instagram.com/accounts/login/ajax/'
    USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'
    session = requests.Session()
    session.headers = {'User-Agent': USER_AGENT, 'X-CSRFToken': 'OHt97SysLsQy47THlx5czgrPxWegLAaV'}

    login_data = {'username': username, 'password': password}
    login = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
    if "sessionid" in login.cookies.get_dict(domain=".instagram.com"):
        session_id = login.cookies.get_dict(domain=".instagram.com")["sessionid"]
        session_id_string = f"sessionid={session_id}"
        settings.update("session_id", session_id_string)
        return True
    else:
        logger.warning("You have entered invalid credentials, please retry.")
        return False

def get_cookie(cookie):
    token = {"cookie": cookie,
             "user-agent": "Instagram 10.3.2 (iPhone7,2; iPhone OS 9_3_3; en_US; en-US; scale=2.00; 750x1334) AppleWebKit/420+",
             "cache-control": "no-cache"}
    return token

def get_media(url, path): urllib.request.urlretrieve(url, path)

def save_cached_id(cached_ids):
    with open(settings.get('cached_ids_path'), "w+") as file:
        json.dump(cached_ids, file)

def get_cached_ids():
    cache_ids_path = settings.get('cached_ids_path')
    if not os.path.exists(cache_ids_path):
        return {}
    with open(cache_ids_path, "r") as file:
        return json.load(file)

def normalize_extra_ids(ids):
    numeric_ids = [elem for elem in ids if elem.isdigit()]
    nicknames = [nick for nick in ids if not nick.isdigit()]
    converted_nicknames = []
    cached_ids = get_cached_ids()
    for nick in nicknames:
        if nick not in cached_ids:
            logger.info(f"Finding id for {nick}")
            time.sleep(randint(1, 4))  # Random delay to avoid requests spamming
            id_of_nickname = nick_to_id(nick)
            cached_ids[nick] = id_of_nickname
        converted_nicknames.append(cached_ids[nick])
    save_cached_id(cached_ids)
    return numeric_ids + converted_nicknames

def get_ids(stories_ids, number_of_persons, extra_ids, ids_mode):
    return (stories_ids[:number_of_persons] if ids_mode != "extra_ids_only" else []) + \
           (extra_ids if ids_mode != "stories_ids_only" else [])

def curr_date():
    year, month, day, _, _ = time.strftime("%Y,%m,%d,%H,%M").split(',')
    return "{}-{}-{}".format(year, month, day)

def time_from_story(element):
    unix_ts = element['taken_at']
    return posix_conv(unix_ts)

def posix_conv(posix_time):
    year, month, day, _, _ = datetime.datetime.utcfromtimestamp(posix_time).strftime("%Y,%m,%d,%H,%M").split(',')
    return "{}-{}-{}".format(year, month, day)

############################## DOWNLOAD AND MANAGE STORIES AND JSON ######################################

def download_today_stories(arr_ids, cookie, folder_path, mode_flag):
    """
    Download user stories. Create subdirectory for each user based on their username and media timestamp
    Ex:
    ig_media/user1/25-08-17
                  /26-08-17
             user2/22-08-17
                  /23-09-17
    Args:
        arr_ids (List): List of ids of people we want to get the stories.
        cookie (dict): Instagram Cookie for authentication in the requests.
    """

    tot_count_img, tot_count_videos = 0, 0

    userid_endpoint = "https://i.instagram.com/api/v1/feed/user/{}/reel_media/"
    for idx, ids in enumerate(arr_ids):
        url = userid_endpoint.format(ids)
        r = requests.get(url, headers=cookie)
        d = r.json()
        if d["status"] == "fail":  # This ensures that bad ids and banned users are skipped
            continue

        if 'items' in d and d['items']:
            items = d['items']
            username = items[0]['user']['username']
        else:
            logger.info("Empty stories for url {}".format(url))
            continue

        logger.info("{}/{} Username: -| {} |-".format(idx + 1, len(arr_ids), username))
        usr_directory = os.path.join(folder_path, username)

        #####

        if not os.path.exists(usr_directory):
            logger.info("Creating Directory :{}".format(usr_directory))
            os.makedirs(usr_directory)
        else:
            logger.info("User already EXIST")

        new_metadata = False  # Used to update the .txt and .json metadata file only if necessary.
        seen_stories_txt = os.path.join(usr_directory, "saved.txt")
        saved_stories_json = os.path.join(usr_directory, f"{username}.json")
        if not os.path.exists(seen_stories_txt) or not os.path.exists(saved_stories_json):
            json_stories_seen, json_stories_saved = set(), []
        else:
            with open(seen_stories_txt, 'r') as seen, open(saved_stories_json, 'r') as saved:
                json_stories_seen = set(seen.read().splitlines())
                json_stories_saved = json.load(saved)

        user_count_i = 0
        user_count_v = 0
        for element in items:
            media_id = element['id']

            date = time_from_story(element)
            time_directory = os.path.join(usr_directory, date)

            if not os.path.exists(time_directory):
                logger.info("Creating Directory :{}".format(time_directory))
                os.makedirs(time_directory)

            """
            MODE FLAGS:
            all: download both media and metadata
            media: download only media
            metadata: download only metadata
            """

            if mode_flag in ["all", "media"]:
                if element['media_type'] == 2:
                    fn_video = os.path.join(time_directory, str(media_id) + ".mp4")
                    if not os.path.isfile(fn_video):
                        videos = element['video_versions']
                        video_url = videos[0]['url']
                        logger.debug("Video URL: {}".format(video_url))
                        get_media(video_url, fn_video)
                        user_count_i += 1
                    else:
                        logger.debug("Video media already saved")

                if element['media_type'] == 1:
                    fn_img = os.path.join(time_directory, str(media_id) + ".jpg")
                    if not os.path.isfile(fn_img):
                        pics = element['image_versions2']['candidates']
                        pic_url = pics[0]['url']
                        logger.debug("Photo URL: {}".format(pic_url))
                        get_media(pic_url, fn_img)
                        user_count_v += 1
                    else:
                        logger.debug("Video media already saved")

            if mode_flag in ["all", "metadata"]:
                if media_id not in json_stories_seen:  # Now save the metadata in a json file
                    json_stories_seen.add(media_id)
                    json_stories_saved.append(element)
                    new_metadata = True
        tot_count_img += user_count_i
        tot_count_videos += user_count_v
        logger.info(f"{len(items)} element(s) in {username} stories, scraped {user_count_i} images and {user_count_v} videos")
        if new_metadata:
            with open(seen_stories_txt, 'w') as seen, open(saved_stories_json, 'w') as saved:
                for id in json_stories_seen:
                    seen.write(f'{id}\n')
                json_stories_saved = json.dump(json_stories_saved, saved)
    logger.info("We finished processing {} users, we downloaded {} IMGs and {} VIDEOs".format(len(arr_ids), tot_count_img, tot_count_videos))
    return tot_count_img, tot_count_videos

def get_stories_tray(cookie):
    """
    Return the response of the API call to the Stories Tray
    Args:
        cookie (dict): Instagram Cookie for authentication in the requests.
    Returns:
        r.json (dict): A dict representation of the instagram response.
    """
    tray_endpoint = "https://i.instagram.com/api/v1/feed/reels_tray/"  # This Endpoint provide unseen stories

    r = requests.get(tray_endpoint, headers=cookie)
    return r.json()

def print_ids_table(usr, ids):
    """
    Print in a nice table the username and the corrisponding id.
    Args:
        usr (List): List of username.
        ids (List): List of ids.
    """
    table_data = [[x, y] for x, y in zip(usr, ids)]
    table_data = [("Username", "ID")] + table_data
    table = AsciiTable(table_data)
    logger.debug(table.table)

def tray_to_ids(stories):
    """
    Extrapolate ids of instagram user that appear in the stories tray.
    Nicely print them in a table before returning them.
    Args:
        stories (dict): A dict representation of the instagram response.
    Returns:
        ids (List): A list of users ids
    """
    usr, ids = [], []
    for element in stories['tray']:
        if element['reel_type'] == "mas_reel": continue  # Skip promotional stories.
        ids.append(element['id'])
        username = element['user']['username']
        usr.append(username)

    if PRINT_TABLE:  # Toggleable option to print the table
        print_ids_table(usr, ids)

    return ids

def nick_to_id(nickname):
    """
    Get corresponding ids from a list of user nicknames.
    Args:
        usr_list (List): List of username.
    Returns:
        ids (List): A list of users ids
    """
    base_url_info = "https://www.instagram.com/{}/?__a=1"
    r = requests.get(base_url_info.format(nickname))
    d = r.json()
    logger.info("{} - ID: {}".format(nickname, d["graphql"]["user"]["id"]))
    return d["graphql"]["user"]["id"]

#################### START SCRAPING FUNCTIONS ###################

def start_scrape(scrape_settings, folder_path, number_of_persons, mode_flag="all", ids_mode="all"):
    cookie = get_cookie(scrape_settings["session_id"])  # The check logic for the existence of "session_id" is on the runner.py and flask_server.py files
    stories = get_stories_tray(cookie)
    stories_ids = tray_to_ids(stories)
    extra_ids = normalize_extra_ids(scrape_settings["extra_ids"] if "extra_ids" in scrape_settings else [])
    if number_of_persons < 0: number_of_persons = len(stories_ids)
    ids = get_ids(stories_ids, number_of_persons, extra_ids, ids_mode)

    logger.info(f"Starting scraping in mode: {mode_flag}, ids source: {ids_mode}")
    count_i, count_v = download_today_stories(ids, cookie, folder_path, mode_flag)
    logger.info("Finished scraping")

    timestampStr = datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S)")

    with open("run_history.log", "a+") as o:
        scraped_users = len(ids)
        o.write(f"Date: {timestampStr} - {scraped_users} people scraped - {count_i} IMGs - {count_v} VIDEOs \n")
