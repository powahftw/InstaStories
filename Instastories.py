import requests
import json
import urllib.request
import os
import time
from datetime import datetime
import settings
import logging
from random import randint

try:
    from terminaltables import AsciiTable
    PRINT_TABLE = True
except ImportError as e:
    PRINT_TABLE = False

logger = logging.getLogger(__name__)

DELAY_BETWEEN_USERS = 2

################# UTILS FUNCTIONS #########################

def craft_cookie(cookie):
    return {"cookie": cookie,
            "user-agent": "Instagram 10.3.2 (iPhone7,2; iPhone OS 9_3_3; en_US; en-US; scale=2.00; 750x1334) AppleWebKit/420+",
            "cache-control": "no-cache"}

def save_cached_ids(cached_ids):
    """
    Dump to file a dictionary with a mapping 'username' -> 'id'
    Used to prevent unecessary requests.
    """
    with open(settings.get('cached_ids_path'), "w+") as file:
        json.dump(cached_ids, file)

def get_cached_ids():
    """
    Load a file and return a dictionary with a mapping 'username' -> 'id'
    """
    cache_ids_path = settings.get('cached_ids_path')
    if not os.path.exists(cache_ids_path):
        return {}
    with open(cache_ids_path, "r") as file:
        return json.load(file)

def normalize_extra_ids(ids):
    """
    Given a list of string, containing both nicknames and ids it normalize them to a list of ids.
    The conversion from a nickname to an id make an IG request, but it's cached for future usage.
    """
    numeric_ids = [elem for elem in ids if elem.isdigit()]
    nicknames = [nick for nick in ids if not nick.isdigit()]
    converted_nicknames = []
    cached_ids = get_cached_ids()
    for nick in nicknames:
        if nick not in cached_ids:
            logger.info(f"Finding id for {nick}")
            time.sleep(randint(1, 4))  # Random delay to avoid requests spamming
            id_of_nick = nick_to_id(nick)
            if id_of_nick is not None:
                cached_ids[nick] = id_of_nick
        if nick in cached_ids: converted_nicknames.append(cached_ids[nick])
    save_cached_ids(cached_ids)
    return numeric_ids + converted_nicknames

def get_ids(stories_ids, user_limit, extra_ids, ids_mode):
    """
    Handle logic for picking the ids to process.
    Args:
        stories_ids (List): List of ids of people we got from the stories tray.
        number_of_persons (number): Cap on how many people we will use from stories tray.
        extra_ids (List): List of others ids we want to get the stories from.
        ids_mode (string): Specify which ids we want to use. extra_ids_only, stories_ids_only or both.
    """
    ids = (stories_ids[:user_limit] if ids_mode != "extra_ids_only" else []) + \
          (extra_ids if ids_mode != "stories_ids_only" else [])
    return list(dict.fromkeys(ids))  # Remove duplicates ids.

############################## TIME UTILS ######################################

def curr_date():
    year, month, day, _, _ = time.strftime("%Y,%m,%d,%H,%M").split(',')
    return "{}-{}-{}".format(year, month, day)

def time_from_story(element):
    unix_ts = element['taken_at']
    return posix_conv(unix_ts)

def posix_conv(posix_time):
    return datetime.utcfromtimestamp(posix_time).strftime("%Y-%m-%d")

def retrieve_media(url, file_path):
    times_to_try = 2
    while times_to_try > 0:
        try:
            urllib.request.urlretrieve(url, file_path)
            logger.info("Media download done with no errors")
            return
        except TimeoutError as err:
            logger.info("A timeout error occurred while trying to download the media: \n {err}")
            logger.info(f"Retrying... {times_to_try}")
            times_to_try -= 1
            time.sleep(5)

############################## DOWNLOAD AND MANAGE STORIES AND JSON ######################################

def download_stories(arr_ids, cookie, folder_path, mode_flag):
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
    class MediaType:
        IMG = 1
        VIDEO = 2

    tot_count_img, tot_count_videos = 0, 0

    userid_endpoint = "https://i.instagram.com/api/v1/feed/user/{}/reel_media/"
    for idx, ids in enumerate(arr_ids):
        time.sleep(DELAY_BETWEEN_USERS)  # Little delay between an user and the next one
        url = userid_endpoint.format(ids)

        # Tries to scrape the user, if it fails it will retry untill success
        completed_scraping = False
        while not completed_scraping:
            try:
                r = requests.get(url, headers=cookie)
                d = r.json()
                completed_scraping = True
            except Exception: # Prevents some request errors
                logger.warning(f'Request error: something was wrong with converting request to json, skipping this user')
                time.sleep(5)

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

        user_count_i, user_count_v = 0, 0
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
                if element['media_type'] == MediaType.VIDEO:
                    fn_video = os.path.join(time_directory, str(media_id) + ".mp4")
                    if not os.path.isfile(fn_video):
                        videos = element['video_versions']
                        video_url = videos[0]['url']
                        logger.debug("Video URL: {}".format(video_url))
                        retrieve_media(video_url, fn_video)
                        user_count_i += 1
                    else:
                        logger.debug("Video media already saved")

                if element['media_type'] == MediaType.IMG:
                    fn_img = os.path.join(time_directory, str(media_id) + ".jpg")
                    if not os.path.isfile(fn_img):
                        pics = element['image_versions2']['candidates']
                        pic_url = pics[0]['url']
                        logger.debug("Photo URL: {}".format(pic_url))
                        retrieve_media(pic_url, fn_img)
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
        logger.info(f"{len(items)} element{'s' if len(items) > 1 else ''} in {username} stories, scraped {user_count_i} images and {user_count_v} videos")
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
    TRAY_ENDPOINT = "https://i.instagram.com/api/v1/feed/reels_tray/"  # This Endpoint provide unseen stories

    r = requests.get(TRAY_ENDPOINT, headers=cookie)
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
    Get corresponding id from a user nicknames.
    Args:
        usr_list (string): Username.
    Returns:
        ids (number): Id
    """
    BASE_URL_PROFILE_INFO = "https://www.instagram.com/{}/?__a=1"
    r = requests.get(BASE_URL_PROFILE_INFO.format(nickname))
    if r.status_code != 404:
        d = r.json()
        logger.info("{} - ID: {}".format(nickname, d["graphql"]["user"]["id"]))
        return d["graphql"]["user"]["id"]
    logger.info(f"User {nickname} can't be found, please check the nickname in extra_ids")
    return None
#################### START SCRAPING FUNCTIONS ###################

def start_scrape(scrape_settings, user_limit, media_mode="all", ids_source="all"):
    cookie = craft_cookie(scrape_settings["session_id"])  # The check logic for the existence of "session_id" is on the runner.py and flask_server.py files
    folder_path = scrape_settings["folder_path"]

    stories_ids = []
    if ids_source != "extra_ids_only":
        stories = get_stories_tray(cookie)
        stories_ids = tray_to_ids(stories)
        if user_limit < 0: user_limit = len(stories_ids)
    extra_ids = normalize_extra_ids(scrape_settings["extra_ids"] if "extra_ids" in scrape_settings else [])
    ids = get_ids(stories_ids, user_limit, extra_ids, ids_source)

    logger.info(f"Starting scraping in mode: {media_mode}, ids source: {ids_source}")
    count_i, count_v = download_stories(ids, cookie, folder_path, media_mode)
    logger.info("Finished scraping")
    settings.completed_scraping()   # Send the signal that the scraping process finished. Used to flush Telegram logging.

    timestampStr = datetime.now().strftime("%d-%b-%Y (%H:%M:%S)")

    with open("run_history.log", "a+") as o:
        scraped_users = len(ids)
        o.write(f"Date: {timestampStr} - {scraped_users} people scraped - {count_i} IMGs - {count_v} VIDEOs \n")

    return {"scraped_media": count_i + count_v}
