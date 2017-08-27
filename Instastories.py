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

def download_today_stories(arr_ids):
    
    url_id = "https://i.instagram.com/api/v1/feed/user/{}/reel_media/"
    
    for ids in arr_ids:
        url = url_id.format(ids)
        
        r = requests.get(url, headers = headers)
        d = r.json()
        
        if d['items']:
            items = d['items']
            username = items[0]['user']['username']
        else:
            print("Empty stories for url{}".format(url))
            continue
    
        print("Username: -| {} |-".format(username))
        usr_directory = os.path.join("ig_media", username)
        if not os.path.exists(usr_directory):
            print("Creating Directory :{}".format(usr_directory))
            os.makedirs(usr_directory)
            
            year, month, day, _, _ = time.strftime("%Y,%m,%d,%H,%M").split(',')
            curr_date = "{}-{}-{}".format(day, month, year)
            
            time_directory = os.path.join(usr_directory, curr_date)
            
            if not os.path.exists(time_directory):  
                print("Creating Directory :{}".format(time_directory))
                os.makedirs(time_directory)
            else:
                print("We already processed this DAY and USER")
                continue
                
        for element in items:
            media_id = element['id']
            if element['media_type'] == 2: 
                videos = element['video_versions']
                video_url = videos[0]['url']
                print("Video URL: {}".format(video_url))
                download_media(video_url, os.path.join(time_directory, str(media_id) + ".mp4"))

            if element['media_type'] == 1: 
                pics = element['image_versions2']['candidates']
                pic_url = pics[0]['url']
                print("Photo URL: {}".format(pic_url))
                download_media(pic_url, os.path.join(time_directory, str(media_id) + ".jpg"))

def get_stories_tray():
    r = requests.get(tray_endpoint, headers = headers)
    #print (json.dumps(r.json(), indent = 2))
    return r.json()

def tray_to_ids(stories):
    usr = [];    ids = []
    for element in stories['tray']:
        print (element['id'])
        ids.append(element['id'])
        username = element['user']['username']
        usr.append(username)
        print ("Username: {}".format(username))
        print ("---")
    return ids
    
stories = get_stories_tray() # Get the json of all the obtainable stories
ids = tray_to_ids(stories)    # From the obtainable stories get the id of friends 
download_today_stories(ids)  # Get stories of each person from their ID








