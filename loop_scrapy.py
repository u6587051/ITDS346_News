import scrapy
import time

class StandardSpider(scrapy.Spider):
    name = 'StandardSpider'
    n = 3
    start_urls = []

    def __init__(self):
        # Generating URLs dynamically based on n
        for i in range(self.n):
            if i == 0:
                self.start_urls.append('https://thestandard.co/category/news/business/')
            else:
                self.start_urls.append(f'https://thestandard.co/category/news/business/page/{i + 1}/')

    def parse(self, response):
        date = response.css('div.date::text').getall()
        date = date[1]
        date = date.strip()
        content = response.css('div.desc::text').get()
        cleaned_content = ''.join([t.strip() for t in content if t.strip()])
        for div in response.css('.caption'):
            yield {
                'title': div.css('h3.news-title a::text').get().strip(),
                'date': date,
                'content_abstract': cleaned_content,
            }
            print('----------------------')
            # time.sleep(0.2)

        # for next_page in response.css('a.next'):
        #     yield response.follow(next_page, self.parse)