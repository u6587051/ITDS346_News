# standard_parser.py
# This module handles all HTML parsing and file saving logic for the crawler.

import os
import time
import random

class StandardParser:
    def __init__(self, base_output_dir):
        """
        Initialize the parser with a directory where parsed articles will be saved.
        """
        self.base_output_dir = base_output_dir

    def parse_listing(self, response):
        """
        Parse the listing (category) page to extract article links, titles, and dates.

        Returns:
            A list of dicts: [{title, link, date}, ...]
        """
        date = response.css('div.date::text').getall()
        date = date[1].strip() if len(date) > 1 else ''
        news_items = response.css('.caption')

        parsed_items = []
        for div in news_items:
            link = div.css('h3.news-title a::attr(href)').get()
            title = div.css('h3.news-title a::text').get()
            if link and title:
                parsed_items.append({
                    'title': title.strip(),
                    'link': link.strip(),
                    'date': date
                })

        return parsed_items

    def parse_details(self, response, metadata):
        """
        Parse the details page of an article and save both the HTML and cleaned text.

        Returns:
            A dictionary with article metadata and file save location.
        """
        time.sleep(2 + random.uniform(0.0, 0.3))  # Polite scraping delay

        full_html = response.body.decode('utf-8')
        all_text = response.css("div.entry-content *::text").getall()
        content = "\n".join([t.strip() for t in all_text if t.strip()])
        ref_links = response.css("div.entry-content a::attr(href)").getall()

        # Use the last part of the URL as the folder name
        link = response.url
        head = link.rstrip("/").split("/")[-1]
        folder_path = os.path.join(self.base_output_dir, head)
        os.makedirs(folder_path, exist_ok=True)

        # Save full HTML
        with open(os.path.join(folder_path, f"{head}.html"), 'w', encoding='utf-8') as f_html:
            f_html.write(full_html)

        # Save parsed metadata + content
        with open(os.path.join(folder_path, f"{head}.txt"), 'w', encoding='utf-8') as f_txt:
            f_txt.write(f"Title: {metadata['title']}\n")
            f_txt.write(f"Date: {metadata['date']}\n")
            f_txt.write(f"Content: {content}\n")
            f_txt.write(f"Ref link: {ref_links}\n")

        return {
            'title': metadata['title'],
            'date': metadata['date'],
            'link': link,
            'html_saved_as': folder_path,
        }
