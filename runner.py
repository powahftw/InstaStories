from Instastories import start_scrape, store_session_id
import argparse, random, time, os

COOKIE_PATH = "token.txt"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TOKEN PATH AND NUMBER OF PEOPLE SCRAPED")
    parser.add_argument("-login", help="Use this argument ONLY for login the first time and generate the session id token", action="store_true", default=None)
    parser.add_argument("-n", metavar="<number of persons>", type=int, help="Insert the number of people to scrape (default is all the people)", default=-1)
    parser.add_argument("-f", metavar="<folder path>", help="Insert the destination folder in which you want to download files", default="ig_media")
    parser.add_argument("-m", metavar="<mode>", choices={"all", "media", "metadata"}, help="Set the scraping mode:\n all: scrape media and metadata\n media: scrape only media\n metadata: scrape only metadata", default="all")
    parser.add_argument("-l", metavar="<loop>", choices={"single", "loop"}, help="Use \"single\" for a single scraping cycle, \"loop\" for keep looping", default="single")
    parser.add_argument("-d", metavar="<delay>", type=int, help="Set the delay (in seconds) between scraping sessions in \"loop\" mode", default= 60 * 60 * 8)
    parser.add_argument("-dp", metavar="<delay variance percentage>", type=int, help="Set minimum and maximum delay variance (in percentage)", default=15)

    args = parser.parse_args()
    number_of_persons, folder_path, mode_flag, loop_flag, base_delay, variance = args.n, args.f, args.m, args.l, args.d, args.dp

    if args.login:
        username = input("Please insert your instagram username: ")
        password = input("Please insert your instagram password: ")
        store_session_id(username, password)

    if os.path.exists("token.txt"):
        running = True
        while running:
            base64_media = start_scrape(COOKIE_PATH, folder_path, number_of_persons, mode_flag)
            if loop_flag == "single": running = False
            elif loop_flag == "loop":
                variance = int(base_delay / 100 * variance)
                delay = base_delay + random.randint(-variance, variance)
                time.sleep(delay)
    else:
        print("You have to login into your instagram account int order to use the scraper, use the \"-login\" argument")

