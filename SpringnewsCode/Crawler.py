import scrapy  # Scrapy library for web crawling
from scrapy.crawler import CrawlerProcess  # To run the crawler
from urllib.parse import urlparse  # For parsing URLs
import os  # For file system operations
from Parser import SpringNewsParser  # Custom parser class
import time  # For adding delays
import random  # For generating random delays

class SpringNewsCrawler:
    def __init__(self, start_num, last_num, base_directory):
        """
        Initializes the crawler with start/end page numbers and the base directory to save data.

        Args:
            start_num (int): The starting page number to crawl.
            last_num (int): The last page number to crawl.
            base_directory (str): The base directory where the output will be saved.
        """
        self.start_num = start_num  # Store the starting page number
        self.last_num = last_num    # Store the last page number
        self.base_directory = base_directory  # Store the base directory path
        self.parser = SpringNewsParser(base_directory)  # Initialize the parser (for handling data extraction and saving)
        self.downloaded_links_file = os.path.join(base_directory, 'downloaded_Springnews_links.txt')  # File to keep track of downloaded URLs
        self.downloaded_links = self.load_downloaded_links()  # Load previously downloaded URLs (to avoid re-downloading)

    def load_downloaded_links(self):
        """
        Loads downloaded links from a file. Creates the file if it doesn't exist.
        This helps the crawler resume or avoid duplicate downloads.
        """
        downloaded_links = set()  # Use a set for efficient checking of downloaded links
        if not os.path.exists(self.downloaded_links_file):
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(self.downloaded_links_file), exist_ok=True)
            # Create the file if it does not exist
            open(self.downloaded_links_file, 'w', encoding='utf-8').close()  # Create an empty file
        with open(self.downloaded_links_file, 'r', encoding='utf-8') as f:
            for line in f:
                downloaded_links.add(line.strip())  # Add each URL to the set (remove any extra whitespace)
        return downloaded_links

    def save_downloaded_links(self, links):
        """
        Saves the set of downloaded links to a file.

        Args:
            links (set): A set containing the URLs that have been downloaded.
        """
        with open(self.downloaded_links_file, 'w', encoding='utf-8') as f:
            for link in links:
                f.write(f"{link}\n")  # Write each link to a new line in the file

    def run(self):
        """
        Starts the crawling process.  Configures Scrapy and initiates the crawl.
        """
        process = CrawlerProcess({  # Configure Scrapy
            'DEFAULT_REQUEST_HEADERS': {  # Set default HTTP headers to mimic a browser
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        })
        time.sleep(2 + random.uniform(0.0, 0.3))  # Add a small random delay to be polite to the server
        # Pass 'self' (the Crawler instance) to the spider so it can access the save_downloaded_links method
        process.crawl(SpringSpider, self.start_num, self.last_num, self.parser, self)
        process.start()  # Start the crawling engine

class SpringSpider(scrapy.Spider):
    """
    A Scrapy Spider to crawl news articles from Spring News.
    """
    name = 'springSpider'  # Unique name for the spider

    def __init__(self, start_num, last_num, parser, crawler_instance, *args, **kwargs):
        """
        Initializes the spider.

        Args:
            start_num (int): Starting page number.
            last_num (int): Ending page number.
            parser (SpringNewsParser):  Instance of the parser class.
            crawler_instance (SpringNewsCrawler): Instance of the crawler class (to access shared data).
            *args:  Additional arguments.
            **kwargs: Keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.start_urls = [(f'https://www.springnews.co.th/news/{i}', i) for i in range(start_num, last_num + 1)]  # Generate URLs to crawl
        self.parser = parser  # Store the parser instance
        self.base_directory = parser.base_directory  # Store the base directory
        self.crawler_instance = crawler_instance  # Store the Crawler instance
        self.downloaded_links = crawler_instance.downloaded_links.copy()  # Create a *copy* to avoid accidental modification
        self.new_downloaded_links = crawler_instance.downloaded_links.copy() # Create a copy for links downloaded in this run

    def start_requests(self):
        """
        This method is called by Scrapy to start the crawling process.
        It generates the initial requests to be sent to the server.
        """
        for url, page_id in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={'page_id': page_id})  # Create a request for each URL

    def parse(self, response):
        """
        This method is the callback function for each request. It's responsible for:
        1.  Extracting data from the response (web page).
        2.  Determining what to do next (e.g., follow links).

        Args:
            response (scrapy.http.Response): The response from the server (the web page).
        """
        page_id = response.meta['page_id']  # Get the page ID from the request's metadata
        redirected_url = response.url  # Get the actual URL (after any redirects)

        # Check if the URL was redirected to the homepage (often means the article doesn't exist)
        if self.parser.is_redirected_to_home(redirected_url):
            self.logger.warning(f"Skipping URL {redirected_url} (Redirected to homepage)")
            return  # Stop processing this URL

        # Check if the URL has already been downloaded (to prevent duplicates)
        if redirected_url in self.downloaded_links:
            self.logger.warning(f"Skipping already downloaded URL: {redirected_url}")
            return  # Skip if already downloaded

        folder_name = self.parser.get_folder_structure(redirected_url, page_id)  # Get the folder structure to save data

        # Delegate the actual parsing and saving of data to the SpringNewsParser class
        item = self.parser.parse_and_save(response, folder_name, page_id, redirected_url)
        yield item  # Yield the parsed data (Scrapy will handle it)

        self.new_downloaded_links.add(redirected_url)  # Add the URL to the set of downloaded links
        self.crawler_instance.save_downloaded_links(self.new_downloaded_links)  # Update the downloaded links file