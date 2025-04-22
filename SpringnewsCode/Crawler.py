import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urlparse
import os
from Parser import SpringNewsParser  # Import the parser

class SpringNewsCrawler:
    def __init__(self, start_num, last_num, base_directory):
        self.start_num = start_num
        self.last_num = last_num
        self.base_directory = base_directory
        self.parser = SpringNewsParser(base_directory)  # Initialize the parser

    def run(self):
        process = CrawlerProcess({
            'DEFAULT_REQUEST_HEADERS': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        })

        process.crawl(SpringSpider, self.start_num, self.last_num, self.parser)  # Pass the parser
        process.start()


class SpringSpider(scrapy.Spider):
    name = 'springSpider'

    def __init__(self, start_num, last_num, parser, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [(f'https://www.springnews.co.th/news/{i}', i) for i in range(start_num, last_num + 1)]
        self.parser = parser  # Receive the parser instance
        self.base_directory = parser.base_directory # Receive base directory for save file

    def start_requests(self):
        for url, page_id in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={'page_id': page_id})

    def parse(self, response):
        page_id = response.meta['page_id']
        redirected_url = response.url

        if self.parser.is_redirected_to_home(redirected_url):
            self.logger.warning(f"Skipping URL {redirected_url} (Redirected to homepage)")
            return

        folder_name = self.parser.get_folder_structure(redirected_url, page_id)

        # Delegate parsing and saving to the parser
        item = self.parser.parse_and_save(response, folder_name, page_id, redirected_url)
        yield item  