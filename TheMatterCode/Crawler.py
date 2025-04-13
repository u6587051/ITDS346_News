import os
import scrapy
from scrapy.crawler import CrawlerRunner
from twisted.internet import defer, reactor
from Parser import StandardParser
from scrapy.http import Request
from scrapy.utils.log import configure_logging

class CustomCrawler:
    def __init__(self, pages=1, base_url="https://thematter.co/category/social/economy",
                 base_directory="/Users/tardi9rad3/Desktop/MahidolU/2024-2_ITDS364",
                 downloaded_links_file='downloaded_links.txt'):
        # Basic setup for the crawler
        self.pages = pages
        self.base_url = base_url
        self.base_directory = base_directory
        self.output_directory = os.path.join(base_directory, "The MATTER")
        os.makedirs(self.output_directory, exist_ok=True)
        self.downloaded_links_path = os.path.join(base_directory, downloaded_links_file)
        self.downloaded_links = self.load_downloaded_links()
        self.new_downloaded_links = set(self.downloaded_links)
        self.count = 0
        self.parser = StandardParser(self.output_directory)

    def load_downloaded_links(self):
        # Load existing links from file
        if os.path.exists(self.downloaded_links_path):
            with open(self.downloaded_links_path, "r", encoding="utf-8") as f:
                return [line.strip() for line in f.readlines()]
        return []

    def save_downloaded_links(self):
        # Save updated list of links
        with open(self.downloaded_links_path, "w", encoding="utf-8") as f:
            for link in sorted(self.new_downloaded_links):
                f.write(link + "\n")

    @defer.inlineCallbacks
    def run(self):
        # Async run for multiple pages
        configure_logging()
        runner = CrawlerRunner()
        deferreds = []
        for i in range(self.pages):
            url = self.base_url if i == 0 else f"{self.base_url}/page/{i+1}/"
            d = runner.crawl(NewsSpider, url=url, controller=self)
            deferreds.append(d)
        yield defer.DeferredList(deferreds)
        self.save_downloaded_links()
        reactor.stop()

class NewsSpider(scrapy.Spider):
    name = "thematter_news"

    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'USER_AGENTS_ENABLED': True,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        },
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Referer': 'https://www.google.com/'
        },
        'DOWNLOAD_DELAY': 2,
        'RETRY_TIMES': 3,
        'USER_AGENT': None,
    }

    def __init__(self, url, controller: CustomCrawler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [url]
        self.controller = controller

    def parse(self, response):
        items = self.controller.parser.parse_listing(response)
        total = len(items)
        print(f"[DEBUG] Found {total} article(s) in listing page.")

        for idx, item in enumerate(items, 1):
            if item['link'] in self.controller.new_downloaded_links:
                continue
            yield Request(url=item['link'],
                          callback=self.parse_details,
                          meta={'item': item, 'idx': idx, 'total': total})

    def parse_details(self, response):
        item = response.meta['item']
        idx = response.meta['idx']
        total = response.meta['total']

        result = self.controller.parser.parse_details(response, item)
        self.controller.new_downloaded_links.add(item['link'])
        self.controller.count += 1
        print(result)
        print(f"{idx} out of {total}")
        yield result