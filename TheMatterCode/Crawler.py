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
    """
    Main controller class that orchestrates the entire crawling process.
    Handles configuration, URL management, and spider execution.
    """
    
    def __init__(self, pages=1, base_url="https://thematter.co/category/social/economy",
                 base_directory="/Users/tardi9rad3/Desktop/MahidolU/2024-2_ITDS364",
                 downloaded_links_file='downloaded_TheMatter_links.txt'):
        """
        Initialize crawler with configuration parameters.
        
        Args:
            pages (int): Number of listing pages to crawl
            base_url (str): Starting URL for the crawl
            base_directory (str): Root directory for output storage
            downloaded_links_file (str): Filename to track crawled URLs
        """
        # Basic configuration setup
        self.pages = pages
        self.base_url = base_url
        self.base_directory = base_directory
        
        # Create dedicated output directory for scraped content
        self.output_directory = os.path.join(base_directory, "The MATTER")
        os.makedirs(self.output_directory, exist_ok=True)
        
        # Initialize URL tracking system
        self.downloaded_links_path = os.path.join(base_directory, downloaded_links_file)
        self.downloaded_links = self.load_downloaded_links()  # Load previously crawled URLs
        self.new_downloaded_links = set(self.downloaded_links)  # Using set for O(1) lookups
        self.count = 0  # Counter for tracking progress
        
        # Initialize the custom content parser
        self.parser = TheMatterParser(self.output_directory)

    def load_downloaded_links(self):
        """
        Load previously crawled URLs from tracking file.
        Maintains continuity between crawling sessions.
        """
        if os.path.exists(self.downloaded_links_path):
            with open(self.downloaded_links_path, "r", encoding="utf-8") as f:
                return [line.strip() for line in f.readlines()]
        return []  # Return empty list if no history exists

    def save_downloaded_links(self):
        """
        Persist crawled URLs to tracking file.
        Ensures we don't re-crawl the same content in future runs.
        """
        with open(self.downloaded_links_path, "w", encoding="utf-8") as f:
            for link in sorted(self.new_downloaded_links):
                f.write(link + "\n")

    @defer.inlineCallbacks
    def run(self):
        """
        Main asynchronous execution method.
        Coordinates the crawling process using Scrapy's CrawlerRunner.
        """
        configure_logging()  # Set up Scrapy's logging system
        runner = CrawlerRunner()  # Create crawler orchestration object
        deferreds = []  # Store asynchronous tasks
        
        # Create crawling tasks for each page number
        for i in range(self.pages):
            # Generate URL for each page (first page is base URL)
            url = self.base_url if i == 0 else f"{self.base_url}/page/{i+1}/"
            
            # Start crawling process for each page
            d = runner.crawl(NewsSpider, url=url, controller=self)
            deferreds.append(d)
        
        # Wait for all crawling tasks to complete
        yield defer.DeferredList(deferreds)
        
        # Finalize the crawling session
        self.save_downloaded_links()  # Persist crawled URLs
        reactor.stop()  # Shut down the async reactor

class NewsSpider(scrapy.Spider):
    """
    Scrapy spider implementation that handles the actual web crawling.
    Contains the logic for navigating pages and extracting content.
    """
    
    name = "thematter_news"  # Unique identifier for this spider

    # Comprehensive spider configuration
    custom_settings = {
        # Respect robots.txt rules (ethical crawling)
        'ROBOTSTXT_OBEY': True,
        
        # Browser-like user agent to avoid bot detection
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        
        # Request throttling configuration
        'DOWNLOAD_DELAY': random.uniform(2.0, 5.0),  # Randomized delay between requests
        'AUTOTHROTTLE_ENABLED': True,  # Enable automatic throttling
        'AUTOTHROTTLE_START_DELAY': 3.0,  # Initial delay in seconds
        'AUTOTHROTTLE_MAX_DELAY': 15.0,  # Maximum allowed delay
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 0.5,  # Conservative request rate
        
        # Error handling and retry logic
        'RETRY_TIMES': 5,  # Number of retry attempts for failed requests
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429],  # Status codes to retry
        
        # Default request headers to mimic browser behavior
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.google.com/',
            'Upgrade-Insecure-Requests': '1',
        },
        
        # Cookie handling configuration
        'COOKIES_ENABLED': True,  # Maintain session state
        'COOKIES_DEBUG': False,  # Disable verbose cookie logging
        
        # Crawling depth limitations
        'DEPTH_LIMIT': 3,  # Maximum link depth to follow
        'DEPTH_PRIORITY': 1,  # Prioritize shallow links
        
        # Caching configuration to reduce server load
        'HTTPCACHE_ENABLED': True,  # Enable response caching
        'HTTPCACHE_EXPIRATION_SECS': 86400,  # Cache lifetime (1 day)
        'HTTPCACHE_DIR': 'httpcache',  # Cache storage location
        'HTTPCACHE_IGNORE_HTTP_CODES': [301, 302, 403, 404, 500],  # Don't cache error responses
    }

    def __init__(self, url, controller: CustomCrawler, *args, **kwargs):
        """
        Initialize spider instance with specific URL and controller reference.
        
        Args:
            url (str): Starting URL for this spider instance
            controller (CustomCrawler): Reference to main controller
        """
        super().__init__(*args, **kwargs)
        self.start_urls = [url]  # URL(s) to start crawling from
        self.controller = controller  # Link to parent controller

    def parse(self, response):
        """
        Parse article listing page to extract individual article links.
        
        Args:
            response: Scrapy response object containing the page HTML
        """
        # Extract article metadata from listing page
        items = self.controller.parser.parse_listing(response)
        total = len(items)
        print(f"[DEBUG] Found {total} article(s) in listing page.")

        # Process each article found on the listing page
        for idx, item in enumerate(items, 1):
            # Skip already processed articles
            if item['link'] in self.controller.new_downloaded_links:
                continue
                
            # Create request for each article's detail page
            yield Request(
                url=item['link'],
                callback=self.parse_details,
                meta={
                    'item': item,  # Pass along article metadata
                    'idx': idx,    # Current article position
                    'total': total # Total articles in this batch
                }
            )

    def parse_details(self, response):
        """
        Parse individual article page to extract full content.
        
        Args:
            response: Scrapy response object containing the article HTML
        """
        # Retrieve metadata passed from listing page
        item = response.meta['item']
        idx = response.meta['idx']
        total = response.meta['total']

        # Use controller's parser to extract and save article content
        result = self.controller.parser.parse_details(response, item)
        
        # Update tracking information
        self.controller.new_downloaded_links.add(item['link'])
        self.controller.count += 1
        
        # Output progress information
        print(result)
        print(f"{idx} out of {total}")
        
        # Yield the result for potential pipeline processing
        yield result