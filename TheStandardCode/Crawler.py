import os
from scrapy.crawler import CrawlerRunner
from scrapy.http import Request
import scrapy
from twisted.internet import defer, reactor
from Parser import StandardParser
import time


#Initialize the crawler with scraping configuration.
class CustomCrawler:
    def __init__(
        self,
        pages=1,
        items=10,
        base_url="https://thestandard.co/category/news/business/",
        base_directory="./newscoma_output",
        downloaded_links_file='downloaded_TheStandard_links.txt'
    ):
        self.start_time = None
        self.finish_time = None
        self.pages = pages
        self.base_url = base_url
        self.base_directory = base_directory
        self.output_directory = os.path.join(base_directory, "Standard 2025")
        self.downloaded_links_file = downloaded_links_file
        self.items = items
        self.downloaded_links_path = os.path.join(base_directory, downloaded_links_file)
        self.downloaded_links = self.load_downloaded_links()
        self.new_downloaded_links = set(self.downloaded_links)

        self.count = 0
        self.parser = StandardParser(self.output_directory)

    #Load links that have already been downloaded (avoid duplicates).
    def load_downloaded_links(self):
        if os.path.exists(self.downloaded_links_path):
            with open(self.downloaded_links_path, 'r', encoding='utf-8') as file:
                return [line.strip() for line in file.readlines()]
        return []

    #Save updated set of downloaded links to file.
    def save_downloaded_links(self):
        with open(self.downloaded_links_path, 'w', encoding='utf-8') as file:
            for link in self.new_downloaded_links:
                file.write(f"{link}\n")

    #Start the crawling process using CrawlerRunner.
    @defer.inlineCallbacks
    def start(self):
        self.start_time = time.time()
        runner = CrawlerRunner()
        for i in range(self.pages):
            url = self.base_url if i == 0 else f"{self.base_url}page/{i + 1}/"
            yield runner.crawl(self.NewsSpider, url, self)
        reactor.stop()

    #A custom Scrapy spider class used by the CustomCrawler. It receives URLs and config dynamically from the controller.
    class NewsSpider(scrapy.Spider):
        name = "custom_news"

        #Initialize the crawler configuration.
        def __init__(self, url, controller: "CustomCrawler", *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.start_urls = [url]
            self.controller = controller

        #Parse the category/listing page and queue article detail pages.
        def parse(self, response):
            parsed_items = self.controller.parser.parse_listing(response)

            #Loop check if url from parsed_items already have in dowload file. It's will skip
            for item in parsed_items:
                if item["link"] in self.controller.new_downloaded_links:
                    print(f"Skipping already downloaded link: {item['link']}")
                    continue

                #Schedule article detail parsing
                yield Request(
                    url=item["link"],
                    callback=self.parse_details,
                    meta=item
                )

        #Parse individual article page, save content, and update downloaded links.
        def parse_details(self, response):
            result = self.controller.parser.parse_details(response, response.meta)
            self.controller.new_downloaded_links.add(response.meta['link'])
            self.controller.count += 1
            self.controller.save_downloaded_links()

            # Log stats
            self.crawler.stats.inc_value('articles_scraped')
            print(result)
            print(f'{self.controller.count} out of {self.controller.pages*self.controller.items}')
            yield result

        #Called when the spider closes. Print out stats.
        def closed(self, reason):
            self.controller.finish_time = time.time()
            elapsed = self.controller.finish_time - self.controller.start_time
            stats = self.crawler.stats.get_stats()
            print("\nCrawling finished.")
            print(f"Total requests made: {stats.get('downloader/request_count', 0)}")
            print(f"Successful responses: {stats.get('downloader/response_status_count/200', 0)}")
            print(f"Error responses: {stats.get('downloader/response_status_count/404', 0)}")
            print(f"Articles scraped: {stats.get('articles_scraped', 0)}")
            print(f"Elapsed time (s): {elapsed:.2f}")
            print(f"Spider closed with reason: {reason}")
