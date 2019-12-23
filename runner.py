from Instastories import start_scrape
import argparse, random, time

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TOKEN PATH AND NUMBER OF PEOPLE SCRAPED")
    parser.add_argument("t", metavar="<token>", help="Insert the path of cookie file")
    parser.add_argument("n", metavar="<number of persons>", type=int, help="Insert the number of people to scrape, use \"0\" to scrape all the users")
    parser.add_argument("f", metavar="<folder path>", help="Insert the destination folder in which you want to download files")
    parser.add_argument("m", metavar="<mode>", choices={"all", "media", "metadata"}, help="Set the scraping mode:\n all: scrape media and metadata\n media: scrape only media\n metadata: scrape only metadata")
    parser.add_argument("l", metavar="<loop>", choices={"single", "loop"}, help="Use \"single\" for a single scraping cycle, \"loop\" for keep looping")
    parser.add_argument("-d", metavar="<delay>", type=int, help="Set the delay between scraping sessions in \"loop\" mode")
    parser.add_argument("-dp", metavar="<delay variance percentage>", type=int, help="Set minimum and maximum delay variance")

    args = parser.parse_args()
    if args.l == "loop" and (args.d is None):
        parser.error("Delay (-d) is required to loop mode")
    cookie_path = args.t 
    number_of_persons = args.n
    folder_path = args.f
    mode_flag = args.m
    loop_flag = args.l
    running = True
    while running:
        base64_media = start_scrape(cookie_path, folder_path, number_of_persons, mode_flag)
        if loop_flag == "single": running = False
        if loop_flag == "loop":
            if args.dp:
                variance = args.dp
            else:
                variance = int(args.d/100*15)
            delay = args.d + random.randint(-variance, variance)
            time.sleep(delay)
