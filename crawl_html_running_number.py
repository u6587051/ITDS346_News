import random
import scrapy
import os

class StandardSpider(scrapy.Spider):
    name = 'standardSpider'
    n = 2
    start_urls = []

    def __init__(self):
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
            link = div.css('h3.news-title a::attr(href)').get().strip()
            yield response.follow(link, self.parse_details, meta={'title': div.css('h3.news-title a::text').get().strip(), 'date': date, 'content_abstract': cleaned_content})

    def parse_details(self, response):
        random_float = random.random() 
        cstring = str(random_float)
        full_html = response.body.decode('utf-8')
        title = response.meta['title']

        base_directory = r"C:\Users\chgun\Desktop\homework\year3\semester 2\Practical Data Science\Standard 2025"
        
        folder_path = os.path.join(base_directory, cstring)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        os.chdir(folder_path)

        filename = f"{cstring}.html"

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(full_html)

        yield {
            'title': title,
            'date': response.meta['date'],
            'content_abstract': response.meta['content_abstract'],
            'link': response.url,
            'html_saved_as': folder_path
        }