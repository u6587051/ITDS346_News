# standard_parser.py
# This module handles all HTML parsing and file saving logic for the crawler.

import os
import time
import random

#Initialize the parser with a directory where parsed articles will be saved.
class StandardParser:
    def __init__(self, base_output_dir):
        self.base_output_dir = base_output_dir
        self.count = 1

    #Parse the listing page to extract article links, titles, and dates.
    def parse_listing(self, response):

        # Clean all date texts: strip spaces, remove empty lines
        dates = [d.strip() for d in response.css('div.date::text').getall() if d.strip()]
        
        news_items = response.css('.caption')

        parsed_items = []
        for idx, div in enumerate(news_items):
            link = div.css('h3.news-title a::attr(href)').get()
            title = div.css('h3.news-title a::text').get()
            date = dates[idx] if idx < len(dates) else ''  # safe fallback if no date

            if link and title:
                parsed_items.append({
                    'title': title.strip(),
                    'link': link.strip(),
                    'date': date
                })

        return parsed_items

    #Parse the details page of an article and save both the HTML and text file.
    def parse_details(self, response, metadata):
        n = self.count
        time.sleep(2 + random.uniform(0.0, 0.3))  # Polite scraping delay

        full_html = response.body.decode('utf-8')
        all_text = response.css("div.entry-content *::text").getall()
        content = "\n".join([t.strip() for t in all_text if t.strip()])
        ref_links = response.css("div.entry-content a::attr(href)").getall()

        link = response.url
        head = link.rstrip("/").split("/")[-1]

        # Add date as a subfolder
        date_folder = metadata['date'].replace('/', '-').replace(':', '-').replace(' ', '_') or 'unknown_date'
        folder_path = os.path.join(self.base_output_dir, date_folder, head)
        sample_path = r"C:\Users\chgun\Desktop\homework\year3\semester2\Practical Data Science\sample_data_evaluation\scraped_content"
        os.makedirs(folder_path, exist_ok=True)

        #Save full HTML
        with open(os.path.join(folder_path, f"{head}.html"), 'w', encoding='utf-8') as f_html:
            f_html.write(full_html)

        #Save parsed metadata + content
        with open(os.path.join(folder_path, f"{head}.txt"), 'w', encoding='utf-8') as f_txt:
            f_txt.write(f"Title: {metadata['title']}\n")
            f_txt.write(f"Date: {metadata['date']}\n")
            f_txt.write(f"Content: {content}\n")
            f_txt.write(f"Ref link: {ref_links}\n")
        
        # # Save sample content for evaluation
        # with open(os.path.join(sample_path, f"file{n}.txt"), 'w', encoding='utf-8') as f_txt:
        #     f_txt.write(f"Content: {content}\n")

        self.count += 1

        return {
            'title': metadata['title'],
            'date': metadata['date'],
            'link': link,
            'html_saved_as': folder_path,
        }
