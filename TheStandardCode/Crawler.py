# custom_crawler.py
# This module defines the main CustomCrawler class that manages scraping flow and controls Scrapy spiders.

import os
from scrapy.crawler import CrawlerRunner
from scrapy.http import Request
import scrapy
from twisted.internet import defer, reactor
from Parser import StandardParser

class CustomCrawler:
    def __init__(
        self,
        pages=1,
        items=10,
        base_url="https://thestandard.co/category/news/business/",
        base_directory=r"C:\Users\chgun\Desktop\homework\year3\semester2\Practical Data Science",
        downloaded_links_file='downloaded_links.txt'
    ):
        """
        Initialize the crawler with scraping configuration.
        """
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

    def load_downloaded_links(self):
        """
        Load links that have already been downloaded (to avoid duplicates).
        """
        if os.path.exists(self.downloaded_links_path):
            with open(self.downloaded_links_path, 'r', encoding='utf-8') as file:
                return [line.strip() for line in file.readlines()]
        return []

    def save_downloaded_links(self):
        """
        Save updated set of downloaded links to file.
        """
        with open(self.downloaded_links_path, 'w', encoding='utf-8') as file:
            for link in self.new_downloaded_links:
                file.write(f"{link}\n")

    @defer.inlineCallbacks
    def start(self):
        """
        Start the crawling process using CrawlerRunner.
        """
        runner = CrawlerRunner()
        for i in range(self.pages):
            url = self.base_url if i == 0 else f"{self.base_url}page/{i + 1}/"
            yield runner.crawl(self.NewsSpider, url, self)
        reactor.stop()

    class NewsSpider(scrapy.Spider):
        """
        A custom Scrapy spider class used by the CustomCrawler.
        It receives URLs and config dynamically from the controller.
        """
        name = "custom_news"

        def __init__(self, url, controller: "CustomCrawler", *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.start_urls = [url]
            self.controller = controller

        def parse(self, response):
            """
            Parse the category/listing page and queue article detail pages.
            """
            parsed_items = self.controller.parser.parse_listing(response)


            for item in parsed_items:
                if item["link"] in self.controller.new_downloaded_links:
                    print(f"Skipping already downloaded link: {item['link']}")
                    continue

                # Schedule article detail parsing
                yield Request(
                    url=item["link"],
                    callback=self.parse_details,
                    meta=item
                )

        def parse_details(self, response):
            """
            Parse individual article page, save content, and update downloaded links.
            """
            result = self.controller.parser.parse_details(response, response.meta)
            self.controller.new_downloaded_links.add(response.meta['link'])
            self.controller.count += 1
            self.controller.save_downloaded_links()
            print(result)
            print(f'{self.controller.count} out of {self.controller.pages*self.controller.items}')
            yield result