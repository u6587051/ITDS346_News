# main.py
# Entry point to run the crawler from the command line or a script.

from Crawler import CustomCrawler
from twisted.internet import reactor

if __name__ == '__main__':
    # Initialize crawler with desired parameters
    crawler = CustomCrawler()  # You can change number of pages or other parameters here

    # Start crawling and run the reactor loop
    crawler.start()
    reactor.run()