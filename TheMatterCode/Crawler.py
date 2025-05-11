# Import necessary libraries
import os  # For file and directory operations
import random  # For generating random delays
import scrapy  # Main Scrapy framework for web crawling
from scrapy.crawler import CrawlerRunner  # To run spiders
from twisted.internet import defer, reactor  # For asynchronous operations
from Parser import TheMatterParser  # Custom parser module (external dependency)
from scrapy.http import Request  # For creating HTTP requests
from scrapy.utils.log import configure_logging  # For logging configuration

class CustomCrawler:
    """Main controller class for managing the crawling process"""
    
    def __init__(self, pages=1, base_url="https://thematter.co/category/social/economy",
                 base_directory="/Users/tardi9rad3/Desktop/MahidolU/2024-2_ITDS364",
                 downloaded_links_file='downloaded_TheMatter_links.txt'):
        """
        Initialize crawler with configuration:
        - pages: Number of pages to crawl
        - base_url: Starting URL for crawling
        - base_directory: Root directory for output files
        - downloaded_links_file: File to store crawled URLs
        """
        # Basic configuration setup
        self.pages = pages
        self.base_url = base_url
        self.base_directory = base_directory
        # Create output directory if it doesn't exist
        self.output_directory = os.path.join(base_directory, "The MATTER")
        os.makedirs(self.output_directory, exist_ok=True)
        # Path management for downloaded links file
        self.downloaded_links_path = os.path.join(base_directory, downloaded_links_file)
        # Load previously downloaded links
        self.downloaded_links = self.load_downloaded_links()
        # Set for new links (avoids duplicates)
        self.new_downloaded_links = set(self.downloaded_links)
        self.count = 0  # Counter for tracking crawled items
        self.parser = TheMatterParser(self.output_directory)  # Initialize parser

    def load_downloaded_links(self):
        """Load previously crawled URLs from file"""
        if os.path.exists(self.downloaded_links_path):
            with open(self.downloaded_links_path, "r", encoding="utf-8") as f:
                return [line.strip() for line in f.readlines()]
        return []  # Return empty list if file doesn't exist

    def save_downloaded_links(self):
        """Save crawled URLs to file for future reference"""
        with open(self.downloaded_links_path, "w", encoding="utf-8") as f:
            for link in sorted(self.new_downloaded_links):
                f.write(link + "\n")

    @defer.inlineCallbacks
    def run(self):
        """Main asynchronous method to run the crawler"""
        configure_logging()  # Set up Scrapy logging
        runner = CrawlerRunner()  # Create crawler runner
        deferreds = []  # List to store deferred objects
        
        # Create crawling tasks for each page
        for i in range(self.pages):
            # Generate URL for each page (first page is base URL)
            url = self.base_url if i == 0 else f"{self.base_url}/page/{i+1}/"
            # Start crawling and add to deferred list
            d = runner.crawl(NewsSpider, url=url, controller=self)
            deferreds.append(d)
        
        # Wait for all crawling tasks to complete
        yield defer.DeferredList(deferreds)
        self.save_downloaded_links()  # Save new links
        reactor.stop()  # Stop the reactor when done

class NewsSpider(scrapy.Spider):
    """Scrapy spider implementation for crawling news articles"""
    
    name = "thematter_news"  # Unique identifier for the spider

    # Custom settings for the spider (overrides project settings)
    custom_settings = {
        # Respect robots.txt rules (good practice)
        'ROBOTSTXT_OBEY': True,
        
        # User-Agent and basic headers to mimic browser
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        
        # Randomized delay and auto-throttling to avoid overwhelming server
        'DOWNLOAD_DELAY': random.uniform(2.0, 5.0),  # Random delay between requests
        'AUTOTHROTTLE_ENABLED': True,  # Enable auto-throttling
        'AUTOTHROTTLE_START_DELAY': 3.0,  # Initial delay
        'AUTOTHROTTLE_MAX_DELAY': 15.0,  # Maximum delay
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 0.5,  # Conservative concurrency
        
        # Retry settings for handling temporary failures
        'RETRY_TIMES': 5,  # Number of retry attempts
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429],  # Status codes to retry
        
        # Default request headers
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.google.com/',
            'Upgrade-Insecure-Requests': '1',
        },
        
        # Cookie handling
        'COOKIES_ENABLED': True,  # Enable cookies for session management
        'COOKIES_DEBUG': False,  # Disable cookie debugging
        
        # Depth limiting to prevent infinite crawling
        'DEPTH_LIMIT': 3,  # Maximum depth to follow links
        'DEPTH_PRIORITY': 1,  # Depth priority
        
        # Cache settings to reduce server load
        'HTTPCACHE_ENABLED': True,  # Enable caching
        'HTTPCACHE_EXPIRATION_SECS': 86400,  # Cache for 1 day
        'HTTPCACHE_DIR': 'httpcache',  # Cache storage directory
        'HTTPCACHE_IGNORE_HTTP_CODES': [301, 302, 403, 404, 500],  # Codes to not cache
    }

    def __init__(self, url, controller: CustomCrawler, *args, **kwargs):
        """Initialize spider with specific URL and controller reference"""
        super().__init__(*args, **kwargs)
        self.start_urls = [url]  # Starting URL(s) for the spider
        self.controller = controller  # Reference to main controller

    def parse(self, response):
        """Parse listing page to extract article links"""
        # Get article items from listing page using controller's parser
        items = self.controller.parser.parse_listing(response)
        total = len(items)
        print(f"[DEBUG] Found {total} article(s) in listing page.")

        # Process each article link
        for idx, item in enumerate(items, 1):
            # Skip already downloaded links
            if item['link'] in self.controller.new_downloaded_links:
                continue
            # Create request for each article
            yield Request(
                url=item['link'],
                callback=self.parse_details,
                meta={'item': item, 'idx': idx, 'total': total}
            )

    def parse_details(self, response):
        """Parse individual article page to extract content"""
        # Get metadata from the request
        item = response.meta['item']
        idx = response.meta['idx']
        total = response.meta['total']

        # Parse article details using controller's parser
        result = self.controller.parser.parse_details(response, item)
        # Update controller state
        self.controller.new_downloaded_links.add(item['link'])
        self.controller.count += 1
        # Print progress and result
        print(result)
        print(f"{idx} out of {total}")
        yield result  # Return parsed data