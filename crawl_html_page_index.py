import scrapy
import os
import time
import random

class StandardSpider(scrapy.Spider):
    name = 'standardSpider'
    pages = 2
    start_urls = []
    total_news = pages*10

    def __init__(self):
        self.count = 0
        for i in range(self.pages):
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

        news_items = response.css('.caption')

        for div in news_items:
            link = div.css('h3.news-title a::attr(href)').get().strip()
            title = div.css('h3.news-title a::text').get().strip()

            yield response.follow(
                link,
                self.parse_details,
                meta={'title': title, 'date': date, 'content_abstract': cleaned_content}
            )

    def parse_details(self, response):
        time.sleep(2 + random.uniform(0.00, 0.3))
        full_html = response.body.decode('utf-8')
        link = response.url
        head = str(link).split("/")
        head = head[-2]

        base_directory = r"C:\Users\chgun\Desktop\homework\year3\semester 2\Practical Data Science\Standard 2025"
        
        folder_path = os.path.join(base_directory, head)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        os.chdir(folder_path)

        filename = f"{head}.html"

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(full_html)
        
        self.count += 1

        yield {
            # 'title': response.meta['title'],
            # 'date': response.meta['date'],
            # 'content_abstract': response.meta['content_abstract'],
            'link': link,
            'html_saved_as': folder_path,
            'count': f'{self.count} out of {self.total_news}',
        }
