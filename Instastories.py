import requests
import json
import urllib.request
from terminaltables import AsciiTable
import os
import time

endpoint = "https://i.instagram.com/api/v1/feed/reels_tray/" # This Endpoint just provide unseen stories

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
        directory = "pic/" + username
        if not os.path.exists(directory):
            print("Creating Directory :{}".format(directory))
            os.makedirs(directory)
            
            year, month, day, _, _ = time.strftime("%Y,%m,%d,%H,%M").split(',')
            curr_date = "{}-{}-{}".format(day, month, year)
            
            if not os.path.exists(directory + "/" + curr_date):  
                print("Creating Directory :{}".format(directory + "/" + curr_date))
                os.makedirs(directory + "/" + curr_date)
            else:
                print("We already processed this DAY and USER")
                continue
                
        for element in items:
            media_id = element['id']
            if element['media_type'] == 2: 
                video = element['video_versions']
                video_url = video[0]['url']
                print("Video URL: {}".format(video_url))
                download_media(video_url,"/" + directory + "/" + curr_date + "/" + str(media_id) + ".mp4")

            if element['media_type'] == 1: 
                pics = element['image_versions2']['candidates']
                pic_url = pics[0]['url']
                print("Photo URL: {}".format(pic_url))
                download_media(pic_url,"/" + directory + "/" + curr_date + "/" + str(media_id) + ".jpg")

def get_stories_tray():
    r = requests.get(endpoint, headers = headers)
    #print (json.dumps(r.json(), indent = 2))
    return r.json()
                
stories = get_stories_tray()

usr = []
ids = []

for element in stories['tray']:
    print (element['id'])
    ids.append(element['id'])
    username = element['user']['username']
    usr.append(username)
    print ("Username: {}".format(username))
    print("---")
    
print("####\n Integrity Check!: {}\n".format(len(usr)==len(set(usr)))) # true

download_today_stories(ids)


