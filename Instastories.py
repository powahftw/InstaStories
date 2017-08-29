import requests
import json
import urllib.request
from terminaltables import AsciiTable
import os
import time

tray_endpoint = "https://i.instagram.com/api/v1/feed/reels_tray/" # This Endpoint just provide unseen stories

headers =      { ############# }

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
    
    url_id = "https://i.instagram.com/api/v1/feed/user/{}/reel_media/"
    
    for idx, ids in enumerate(arr_ids):
        url = url_id.format(ids)
        
        r = requests.get(url, headers = headers)
        d = r.json()
        
        if d['items']:
            items = d['items']
            username = items[0]['user']['username']
        else:
            print("Empty stories for url{}".format(url))
            continue
    
        print("{}/{} Username: -| {} |-".format(idx+1, len(arr_ids), username))
        usr_directory = os.path.join("ig_media", username)
        
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
                else:
                    print("Video media already saved")

            if element['media_type'] == 1: 
                filename = os.path.join(time_directory, str(media_id) + ".jpg")
                if not os.path.isfile(filename):
                    pics = element['image_versions2']['candidates']
                    pic_url = pics[0]['url']
                    print("Photo URL: {}".format(pic_url))
                    download_media(pic_url, filename)
                else:
                    print("Video media already saved")
            
def get_stories_tray():
    r = requests.get(tray_endpoint, headers = headers)
    #print (json.dumps(r.json(), indent = 2))
    return r.json()

def print_ids_table(usr, ids):
    table_data = [[x,y] for x, y in zip(usr, ids)]
    table_data = [("Username", "ID")] + table_data
    table = AsciiTable(table_data)
    print (table.table)

def tray_to_ids(stories):
    usr = [];    ids = []
    for element in stories['tray']:
        ids.append(element['id'])
        username = element['user']['username']
        usr.append(username)
        
    if PRINT_TABLE:
        print_ids_table(usr, ids)
    
    return ids
    
stories = get_stories_tray() # Get the json of all the obtainable stories
ids = tray_to_ids(stories)    # From the obtainable stories get the id of friends 
download_today_stories(ids)  # Get stories of each person from their ID






