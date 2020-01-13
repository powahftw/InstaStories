from Instastories import start_scrape
import argparse, random, time

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TOKEN PATH AND NUMBER OF PEOPLE SCRAPED")
    parser.add_argument("t", metavar="<token>", help="Insert the path of cookie file")
    parser.add_argument("-n", metavar="<number of persons>", type=int, help="Insert the number of people to scrape (default is all the people)", default=-1)
    parser.add_argument("f", metavar="<folder path>", help="Insert the destination folder in which you want to download files")
    parser.add_argument("m", metavar="<mode>", choices={"all", "media", "metadata"}, help="Set the scraping mode:\n all: scrape media and metadata\n media: scrape only media\n metadata: scrape only metadata")
    parser.add_argument("l", metavar="<loop>", choices={"single", "loop"}, help="Use \"single\" for a single scraping cycle, \"loop\" for keep looping")
    parser.add_argument("-d", metavar="<delay>", type=int, help="Set the delay (in seconds) between scraping sessions in \"loop\" mode", default= 28800)
    parser.add_argument("-dp", metavar="<delay variance percentage>", type=int, help="Set minimum and maximum delay variance (in percentage)", default=15)

    args = parser.parse_args()
    cookie_path, number_of_persons, folder_path, mode_flag, loop_flag, base_delay, variance = args.t, args.n, args.f, args.m, args.l, args.d, args.dp
    running = True
    while running:
        base64_media = start_scrape(cookie_path, folder_path, number_of_persons, mode_flag)
        if loop_flag == "single": running = False
        elif loop_flag == "loop":
            variance = int(base_delay/100*variance)
            delay = base_delay + random.randint(-variance, variance)
            print(delay)
            time.sleep(delay)
