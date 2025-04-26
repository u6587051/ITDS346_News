import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urlparse
import os
from Parser import SpringNewsParser  # Import the parser
import time
import random


class SpringNewsCrawler:
    def __init__(self, start_num, last_num, base_directory):
        self.start_num = start_num
        self.last_num = last_num
        self.base_directory = base_directory
        self.parser = SpringNewsParser(base_directory)  # Initialize the parser
        self.downloaded_links_file = os.path.join(base_directory, 'downloaded_links.txt')
        self.downloaded_links = self.load_downloaded_links()  # Load downloaded links

    def load_downloaded_links(self):
        """Loads downloaded links from a file, creates the file if it doesn't exist."""
        downloaded_links = set()
        if not os.path.exists(self.downloaded_links_file):
            # Create the file if it does not exist
            os.makedirs(os.path.dirname(self.downloaded_links_file), exist_ok=True)  # Ensure directory exists
            open(self.downloaded_links_file, 'w', encoding='utf-8').close()
        with open(self.downloaded_links_file, 'r', encoding='utf-8') as f:
            for line in f:
                downloaded_links.add(line.strip())
        return downloaded_links

    def save_downloaded_links(self, links):
        """Saves downloaded links to a file."""
        with open(self.downloaded_links_file, 'w', encoding='utf-8') as f:
            for link in links:
                f.write(f"{link}\n")

    def run(self):
        process = CrawlerProcess({
            'DEFAULT_REQUEST_HEADERS': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        })
        time.sleep(2 + random.uniform(0.0, 0.3))
        # Pass self to the spider so it can access the save_downloaded_links method
        process.crawl(SpringSpider, self.start_num, self.last_num, self.parser, self)  
        process.start()



class SpringSpider(scrapy.Spider):
    name = 'springSpider'

    def __init__(self, start_num, last_num, parser, crawler_instance, *args, **kwargs): # เพิ่ม crawler_instance
        super().__init__(*args, **kwargs)
        self.start_urls = [(f'https://www.springnews.co.th/news/{i}', i) for i in range(start_num, last_num + 1)]
        self.parser = parser
        self.base_directory = parser.base_directory
        self.crawler_instance = crawler_instance # เก็บ instance ของ Crawler
        self.downloaded_links = crawler_instance.downloaded_links.copy() # ใช้สำเนาที่นี่ด้วย
        self.new_downloaded_links = crawler_instance.downloaded_links.copy()

    def start_requests(self):
        for url, page_id in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={'page_id': page_id})

    def parse(self, response):
        page_id = response.meta['page_id']
        redirected_url = response.url

        if self.parser.is_redirected_to_home(redirected_url):
            self.logger.warning(f"Skipping URL {redirected_url} (Redirected to homepage)")
            return

        if redirected_url in self.downloaded_links:
            self.logger.warning(f"Skipping already downloaded URL: {redirected_url}")
            return

        folder_name = self.parser.get_folder_structure(redirected_url, page_id)

        # Delegate parsing and saving to the parser
        item = self.parser.parse_and_save(response, folder_name, page_id, redirected_url)
        yield item

        self.new_downloaded_links.add(redirected_url)
        # เรียกใช้ save_downloaded_links จาก instance ที่เก็บไว้
        self.crawler_instance.save_downloaded_links(self.new_downloaded_links)
