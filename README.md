# InstaStories
Simple web app to get and save users stories from IG.
It's useful to archive your friends stories!  

It saves the images and videos in a subdirectory structure based on username/date/story_id.

It also offers a way to visualize them in your browser.

### Prerequisites
This script make uses of some libraries, you can install them all using ```pip -r requirements.txt```.

### Running and testing
To start the web app use just run ```python flask_server.py```.

You can then access the page in your browser at: ```127.0.0.1:5000``` (you can also change the port inside the code)

![Index page screenshot](/screenshots/index.PNG "Index page")

## Login
To start using this tool you have to provide your IG cookie: the easiest way to do this is login in settings page with your IG account

Alternatively you can put your session_id code manually in a settings file called ```settings.json``` that you have to create inside the root folder and put:
```{"session_id": "sessionid=<your session id>"}``` inside it

To get it simply use Chrome Dev Tools while visiting [Instagram](instagram.com) and copy the session_id you are sending to them.

## Features
There are different scraping features you can set before starting: 

You can choose to scrape one single time or keep it looping.

You can download media files, json files or both.

You can choose if you want to scrape only the followed people and/or extra people in ```EXTRA IDS``` tab in settings.

## Changing settings
In the settings page you can modify some settings:

    - Download Folder path: this path is where your downloaded media will be saved.
    - Delay between cycles: if you are running in loop mode you can set the interval between every cycle.
    - Variation of the delay: you can set the variation of the loop interval in percentage
    - Extra nicknames/IDS: you can put additional nicknames/IDS to be gathered (one per line)

## Built With

* [Flask](https://flask.palletsprojects.com/en/1.1.x/) - The micro web framework used
