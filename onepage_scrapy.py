import scrapy

class StandardSpider(scrapy.Spider):
    name = 'StandardSpider'
    start_urls = ['https://thestandard.co/new-gen-investor-ep-38-2/']

    def parse(self, response):
            paragraphs = [p.strip() for p in response.css('div.entry-content p::text').getall() if p.strip()]
            yield {
                'title': response.css('div.entry-title h1::text').get(),
                'category': response.css('div.entry-meta > span.category > a::text').getall(),
                'content': paragraphs,
                'author': response.css('div.meta-author a::text').get().strip(),
                'date': response.css('div.meta-date span::text').get()
                }