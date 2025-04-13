from Crawler import CustomCrawler
from twisted.internet import reactor

# Entry point to the program
if __name__ == '__main__':
    crawler = CustomCrawler(pages=1)  # Create a crawler for 1 page
    crawler.run()  # Start crawling
    reactor.run()  # Run Twisted event loop (needed for async crawling)