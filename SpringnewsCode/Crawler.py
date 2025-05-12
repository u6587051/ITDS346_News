import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urlparse
import os
from Parser import SpringNewsParser
import time
import random

class SpringNewsCrawler:
    def __init__(self, base_directory="./newscoma_output"):
        self.base_directory = base_directory
        self.parser = SpringNewsParser(base_directory)
        self.downloaded_links_file = os.path.join(base_directory, 'downloaded_SpringNews_links.txt')
        self.downloaded_links, self.start_num = self.load_downloaded_links()

    def load_downloaded_links(self):
        downloaded_links = set()
        start_num = 1
        if not os.path.exists(self.downloaded_links_file):
            os.makedirs(os.path.dirname(self.downloaded_links_file), exist_ok=True)
            open(self.downloaded_links_file, 'w', encoding='utf-8').close()
        else:
            try:
                with open(self.downloaded_links_file, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line:
                        # Extract the number at the end of the line
                        start_num_str = first_line.split('/')[-1]
                        start_num = int(start_num_str)
                    for line in f:
                        downloaded_links.add(line.strip())
            except ValueError:
                print("Warning: Invalid start_num in downloaded_links_file. Using default start_num = 1")
            except FileNotFoundError:
                print("Warning: downloaded_links_file not found. Using default start_num = 1")
        return downloaded_links, start_num

    def save_downloaded_links(self, links, next_start_num):
        with open(self.downloaded_links_file, 'w', encoding='utf-8') as f:
            f.write(f"") # added source to the saved file
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
        start_num = self.start_num
        last_num = start_num + 1000 #Prevent more news from disappearing than usual
        process.crawl(SpringSpider, start_num, last_num, self.parser, self)
        process.start()


class SpringSpider(scrapy.Spider):
    name = 'springSpider'

    def __init__(self, start_num, last_num, parser, crawler_instance, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [(f'https://www.springnews.co.th/news/{i}', i) for i in range(start_num, last_num + 1)]
        self.parser = parser
        self.base_directory = parser.base_directory
        self.crawler_instance = crawler_instance
        self.downloaded_links = crawler_instance.downloaded_links.copy()
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

        folder_name = self.parser.get_folder_structure(response, page_id)

        item = self.parser.parse_and_save(response, page_id, redirected_url)
        yield item

        self.new_downloaded_links.add(redirected_url)
        self.crawler_instance.save_downloaded_links(self.new_downloaded_links, page_id + 1)