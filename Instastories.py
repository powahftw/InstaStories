import requests
import json
import urllib.request
import os
import time
import datetime
import base64

try:
    from terminaltables import AsciiTable
    PRINT_TABLE = True
except ImportError as e:
    PRINT_TABLE = False


EXTRA_ID = [None] # Get stories from unfollowed users by using their ID
#EXTRA_USR = ["xxxx", "yyyy", "zzzz"] # Get stories from unfollowed users by using their Nicknames, deprecated due to Instagram changes


################# UTILS FUNCTIONS #########################
def get_session_id(username, password):
    LOGIN_URL = 'https://www.instagram.com/accounts/login/ajax/'
    USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'
    session = requests.Session()
    session.headers = {'User-Agent': USER_AGENT}
    session.headers.update({'X-CSRFToken': 'NMFp6WC8vn1tM9qUzm2jRZqq17CWwpzz'})
    login_data = {'username': username, 'password': password}
    login = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
    try:
        session_id = "sessionid=" + login.cookies.get_dict(domain=".instagram.com")["sessionid"]
        with open("token.txt", "w") as token:
            token.write(session_id)
        return 0
    except:
        print("You have entered invalid credentials, please retry.")        
        return 1

def get_cookie(cookie_path):
    token =      {
             "cookie": None,
             "user-agent": "Instagram 10.3.2 (iPhone7,2; iPhone OS 9_3_3; en_US; en-US; scale=2.00; 750x1334) AppleWebKit/420+",
             "cache-control": "no-cache" }

    with open(cookie_path, "r") as f:
        token["cookie"] = f.read()
        return token


def get_media(url, path, media_type, username):
    urllib.request.urlretrieve(url, path)
    with open(path, "rb") as image:
        base64_media = (base64.b64encode(image.read()).decode("utf-8"), media_type, username)
        return base64_media

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

def download_today_stories(arr_ids, cookie, folder_path, number_of_persons, mode_flag):
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

    count_i, count_v = 0, 0
    base64_media = []
    
    userid_endpoint = "https://i.instagram.com/api/v1/feed/user/{}/reel_media/"
    if number_of_persons < 0: number_of_persons = len(arr_ids)
    for idx, ids in enumerate(arr_ids[:number_of_persons]):
        url = userid_endpoint.format(ids)
        
        r = requests.get(url, headers = cookie)
        d = r.json()
        
        if 'items' in d and d['items']:
            items = d['items']
            username = items[0]['user']['username']
        else:
            print("Empty stories for url {}".format(url))
            continue
    
        print("{}/{} Username: -| {} |-".format(idx+1, len(arr_ids), username))
        usr_directory = os.path.join(folder_path, username)
        
        #####
       
        if not os.path.exists(usr_directory):
            print("Creating Directory :{}".format(usr_directory))
            os.makedirs(usr_directory)
        else:
            print("User already EXIST")
        
        for element in items:
            
            media_id = element['id']
            
            date = time_from_story(element)
            time_directory = os.path.join(usr_directory, date)
               
            if not os.path.exists(time_directory):  
                print("Creating Directory :{}".format(time_directory))
                os.makedirs(time_directory)
                
            new_media = True
            

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
                        print("Video URL: {}".format(video_url))
                        base64_media.append(get_media(video_url, fn_video,"video/mp4", username))

                        count_v += 1
                    else:
                        new_media = False
                        print("Video media already saved")

                if element['media_type'] == 1: 
                    fn_img = os.path.join(time_directory, str(media_id) + ".jpg")
                    if not os.path.isfile(fn_img):
                        pics = element['image_versions2']['candidates']
                        pic_url = pics[0]['url']
                        print("Photo URL: {}".format(pic_url))
                        base64_media.append(get_media(pic_url, fn_img, "img/png", username))
                        count_i += 1
                    else:
                        new_media = False
                        print("Video media already saved")
                    
            if mode_flag in ["all", "metadata"]:
                if new_media: # Now save the metadata in a json file 
                    fn_json = os.path.join(time_directory, "json_log" + ".json")
                    with open(fn_json, "a+") as log:
                        log.write(json.dumps(element))
    
    print("We finished processing {} users, we downloaded {} IMGs and {} VIDEOs".format(len(arr_ids[:number_of_persons]), count_i, count_v)) 
    return count_i, count_v, base64_media
    
def get_stories_tray(cookie):
    """
    Return the response of the API call to the Stories Tray
    Args:
        cookie (dict): Instagram Cookie for authentication in the requests.
    Returns:
        r.json (dict): A dict representation of the instagram response.
    """
    tray_endpoint = "https://i.instagram.com/api/v1/feed/reels_tray/" # This Endpoint provide unseen stories
    
    r = requests.get(tray_endpoint, headers = cookie)
    return r.json()

def print_ids_table(usr, ids):
    """
    Print in a nice table the username and the corrisponding id.
    Args:
        usr (List): List of username.
        ids (List): List of ids.
    """
    table_data = [[x,y] for x, y in zip(usr, ids)]
    table_data = [("Username", "ID")] + table_data
    table = AsciiTable(table_data)
    print (table.table)

def tray_to_ids(stories):
    """
    Extrapolate ids of instagram user that appear in the stories tray.
    Nicely print them in a table before returning them.
    Args:
        stories (dict): A dict representation of the instagram response.
    Returns:
        ids (List): A list of users ids
    """
    usr = [];    ids = []
    for element in stories['tray']:
        ids.append(element['id'])
        username = element['user']['username']
        usr.append(username)
        
    if PRINT_TABLE: # Toggleable option to print the table
        print_ids_table(usr, ids)
    
    return ids

def nicks_to_ids(usr_list):
    """
    Get corresponding ids from a list of user nicknames.
    Args:
        usr_list (List): List of username.
    Returns:
        ids (List): A list of users ids
    """
    base_url_info = "https://www.instagram.com/{}/?__a=1"
    ids = []
    for user in usr_list:
        r = requests.get(base_url_info.format(user))
        d = r.json()
        print(d["graphql"]["user"]["edge_followed_by"]["count"])
        print("{} - ID: {}".format(user, d["graphql"]["user"]["id"]))
        ids.append(d["graphql"]["user"]["id"])
    return ids   

#################### START SCRAPING FUNCTIONS ###################

def start_scrape(cookie_path, folder_path, number_of_persons, mode_flag = "all"):
    cookie = get_cookie(cookie_path)
    stories = get_stories_tray(cookie)                                        
    ids = tray_to_ids(stories)                                              
    count_i, count_v, base64_media = download_today_stories(ids , cookie, folder_path, number_of_persons, mode_flag) 

    timestampStr = datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S)")

    with open("run_history.log", "a+") as o:
        if number_of_persons < 0:
            scraped_users = len(ids)
        else:
            scraped_users = number_of_persons
        o.write("Date: {} - {} people scraped - {} IMGs - {} VIDEOs \n".format(timestampStr, scraped_users, count_i, count_v))   
    return base64_media
