from Instastories import start_scrape, login_and_store_session_id
import argparse
import random
import time
import settings
import getpass
import logging


settings.setup_logger()
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TOKEN PATH AND NUMBER OF PEOPLE SCRAPED")
    parser.add_argument("-login", help="Use this argument ONLY for login the first time and generate the session id token", action="store_true", default=None)
    parser.add_argument("-n", metavar="<number of persons>", type=int, help="Insert the number of people to scrape (default is all the people)", default=-1)
    parser.add_argument("-f", metavar="<folder path>", help="Insert the destination folder in which you want to download files", default="ig_media")
    parser.add_argument("-m", metavar="<mode>", choices={"all", "media", "metadata"}, help="Set the scraping mode:\n all: scrape media and metadata\n media: scrape only media\n metadata: scrape only metadata", default="all")
    parser.add_argument("-ids", metavar="<ids source>", choices={"all", "stories_ids_only", "extra_ids_only"}, default="all", help="Set the source of ids:\n all: scrapes users from stories tray and from extra_ids\n stories: scrapes users from stories tray only\n extra: scrapes users from extra_ids only")
    parser.add_argument("-l", metavar="<loop>", choices={"single", "loop"}, help="Use \"single\" for a single scraping cycle, \"loop\" for keep looping", default="single")
    parser.add_argument("-d", metavar="<delay>", type=int, help="Set the delay (in seconds) between scraping sessions in \"loop\" mode", default=60 * 60 * 8)
    parser.add_argument("-dp", metavar="<delay variance percentage>", type=int, help="Set minimum and maximum delay variance (in percentage)", default=15)

    args = parser.parse_args()
    number_of_persons, folder_path, mode_flag, ids_type_flag, loop_flag, base_delay, variance = args.n, args.f, args.m, args.ids, args.l, args.d, args.dp
    is_user_logged_in = settings.has_setting("session_id")

    if args.login and not is_user_logged_in:
        username = input("Username: ")
        password = getpass.getpass()
        login_and_store_session_id(username, password)
    else:
        logger.info("You are already logged in, start scraping")

    if is_user_logged_in:
        running = True
        while running:
            base64_media = start_scrape(settings.get(), folder_path, number_of_persons, mode_flag, ids_type_flag)
            if loop_flag == "single": running = False
            elif loop_flag == "loop":
                variance = int(base_delay / 100 * variance)
                delay = base_delay + random.randint(-variance, variance)
                time.sleep(delay)
    else:
        logger.warning("You have to login into your instagram account int order to use the scraper, use the \"-login\" argument")
