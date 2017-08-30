import requests
import json
import urllib.request
from terminaltables import AsciiTable
import os
import time
import datetime

PRINT_TABLE = True

COOKIE =      {  ######  }

def download_media(url, path):
    urllib.request.urlretrieve(url, path)

def curr_date():
    year, month, day, _, _ = time.strftime("%Y,%m,%d,%H,%M").split(',')
    return "{}-{}-{}".format(day, month, year)

def time_from_story(element):
    unix_ts = element['taken_at']
    return posix_conv(unix_ts)

def posix_conv(posix_time):
    year, month, day, _, _ = datetime.datetime.utcfromtimestamp(posix_time).strftime("%Y,%m,%d,%H,%M").split(',')
    return "{}-{}-{}".format(day, month, year)

def download_today_stories(arr_ids):
    """
    Download user stories. Create subdirectory for each user based on their username and media timestamp
    Ex:
    ig_media/user1/25-08-17
                  /26-08-17
             user2/22-08-17
                  /23-09-17
    Args:
        arr_ids (List): List of ids of people we want to get the stories.
    """
    FOLDER = "ig_media"
    
    count_i, count_v = 0, 0
    
    userid_endpoint = "https://i.instagram.com/api/v1/feed/user/{}/reel_media/"
    
    for idx, ids in enumerate(arr_ids):
        url = userid_endpoint.format(ids)
        
        r = requests.get(url, headers = headers)
        d = r.json()
        
        if d['items']:
            items = d['items']
            username = items[0]['user']['username']
        else:
            print("Empty stories for url{}".format(url))
            continue
    
        print("{}/{} Username: -| {} |-".format(idx+1, len(arr_ids), username))
        usr_directory = os.path.join(FOLDER, username)
        
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
                
            if element['media_type'] == 2: 
                filename = os.path.join(time_directory, str(media_id) + ".mp4")
                if not os.path.isfile(filename): 
                    videos = element['video_versions']
                    video_url = videos[0]['url']
                    print("Video URL: {}".format(video_url))
                    download_media(video_url, filename)
                    count_v += 1
                else:
                    print("Video media already saved")

            if element['media_type'] == 1: 
                filename = os.path.join(time_directory, str(media_id) + ".jpg")
                if not os.path.isfile(filename):
                    pics = element['image_versions2']['candidates']
                    pic_url = pics[0]['url']
                    print("Photo URL: {}".format(pic_url))
                    download_media(pic_url, filename)
                    count_i += 1
                else:
                    print("Video media already saved")
    
    print("We finished processing {} users, we downloaded {} IMGs and {} VIDEOs".format(len(arr_ids), count_i, count_v))       
            
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
        
    if PRINT_TABLE:
        print_ids_table(usr, ids)
    
    return ids
    
stories = get_stories_tray(COOKIE) # Get the json of all the obtainable stories
ids = tray_to_ids(stories)         # From the obtainable stories get the id of friends 
download_today_stories(ids)        # Get stories of each person from their ID






