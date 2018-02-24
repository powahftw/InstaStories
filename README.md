# InstaStories
Simple script to get and save current friends stories from IG.
It's useful to archive your friends stories!  

It saves the images and videos in subfolder based on username and time-stamp from the stories

EDIT: Now work with ISO Date, to convert from the old format i created a small gists [here](https://gist.github.com/powahftw/0a9d4fbb05c698170d6ec0591a721449)
EDIT2: Now works both with extra users ids and nicknames, to get stories from people you don't follow.

### Prerequisites

This script make uses of the requests library and terminaltables for pretty printing of some datas

### Cookie

You will need to provide your IG Cookies to make the script authenticate the request to the api.

To get them simply use Chrome Dev Tools while visiting instagram.com and copy the cookie you are sending to them.


