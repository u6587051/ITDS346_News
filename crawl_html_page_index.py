import scrapy

class BKKbizSpider(scrapy.Spider):
    name = 'bkkbizSpider'
    start_urls = ["https://www.bangkokbiznews.com/business/economic"]

    def start_requests(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        for url in self.start_urls:
            yield scrapy.Request(url, headers=headers, callback=self.parse)

    def parse(self, response):
            for div in response.css('.card-h '):
                yield {
                    "title": div.css('div.card-h-content > h3.card-h-content-title  text-excerpt-2 a::text').get()
                }

