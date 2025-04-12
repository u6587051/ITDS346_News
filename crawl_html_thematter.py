import scrapy
import os
import time
import random

class StandardSpider(scrapy.Spider):
    name = 'standardSpider'
    pages = 1
    start_urls = []
    total_news = pages * 10
    downloaded_links_file = 'downloaded_links.txt'  # File to store the list of downloaded URLs
    base_directory = "/Users/tardi9rad3/Desktop/MahidolU/2024-2_ITDS361"
    
    def __init__(self):
        self.count = 0
        self.downloaded_links_path = os.path.join(self.base_directory, self.downloaded_links_file)
        
        self.downloaded_links = self.load_downloaded_links()  
        
        self.new_downloaded_links = set(self.downloaded_links)

        for i in range(self.pages):
            if i == 0:
                self.start_urls.append('https://thematter.co/category/social/economy')
            else:
                self.start_urls.append(f'https://thematter.co/category/social/economy/page/{i + 1}/')

    def load_downloaded_links(self):
        """Load the list of previously downloaded links from the file."""
        if os.path.exists(self.downloaded_links_path):
            with open(self.downloaded_links_path, 'r', encoding='utf-8') as file:
                return [line.strip() for line in file.readlines()]
        return []

    def save_downloaded_links(self):
        """Save the list of downloaded links to the file."""
        with open(self.downloaded_links_path, 'w', encoding='utf-8') as file:
            for link in self.new_downloaded_links:
                file.write(f"{link}\n")

    def parse(self, response):
        date = response.css('div.date::text').getall()
        date = date[1].strip() if len(date) > 1 else ''
        news_items = response.css('.caption')

        for div in news_items:
            link = div.css('h3.news-title a::attr(href)').get().strip()
            title = div.css('h3.news-title a::text').get().strip()

            if link in self.new_downloaded_links:
                print(f"Skipping already downloaded link: {link}")
                continue

            yield response.follow(
                link,
                self.parse_details,
                meta={'title': title, 'date': date, 'link': link}
            )

    def parse_details(self, response):
        time.sleep(2 + random.uniform(0.00, 0.3))
        full_html = response.body.decode('utf-8')
        link = response.url
        head = str(link).split("/")[-2]
        all_text = response.css("div.entry-content *::text").getall()
        content = "\n".join([t.strip() for t in all_text if t.strip()])
        ref_links = response.css("div.entry-content a::attr(href)").getall()

        base_directory = "/Users/tardi9rad3/Desktop/MahidolU/2024-2_ITDS361"
        folder_path = os.path.join(base_directory, "The Matter", head)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        filename_html = os.path.join(folder_path, f"{head}.html")
        with open(filename_html, 'w', encoding='utf-8') as file:
            file.write(full_html)

        filename_txt = os.path.join(folder_path, f"{head}.txt")
        with open(filename_txt, 'w', encoding='utf-8') as txt_file:
            txt_file.write(f"Title: {response.meta['title']}\n")
            txt_file.write(f"Date: {response.meta['date']}\n")
            txt_file.write(f"Content: {content}\n")
            txt_file.write(f"Ref link: {ref_links}\n")

        self.new_downloaded_links.add(response.meta['link'])
        self.count += 1

        self.save_downloaded_links()

        yield {
            'title': response.meta['title'],
            'date': response.meta['date'],
            'link': link,
            'html_saved_as': folder_path,
            'count': f'{self.count} out of {self.total_news}',
        }