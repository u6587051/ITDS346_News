# Import the custom crawler class that contains all the crawling logic
from Crawler import CustomCrawler

# Import Twisted's reactor which is the core event loop for asynchronous operations
from twisted.internet import reactor

# Entry point to the program - standard Python idiom for main execution
if __name__ == '__main__':
    # Main execution block that runs when the script is executed directly.
    # This is the starting point of the web crawling application.
    
    # Initialize the crawler with configuration
    # - pages=1: Only crawl the first page of listings
    # - Other parameters use default values from CustomCrawler
    crawler = CustomCrawler(pages=1)  # Create crawler instance for 1 page
    
    # Start the crawling process
    # This kicks off the asynchronous operations but doesn't block execution
    crawler.run()  # Begin crawling process
    
    # Start the Twisted reactor event loop
    # This keeps the program running until all asynchronous operations complete
    # The reactor handles all the networking and callbacks in the background
    reactor.run()  # Run the async event loop