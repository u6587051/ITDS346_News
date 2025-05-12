"""
This module contains a web parser for The Matter news website.
It includes functionality to parse article listings and details, save content to files,
and manually parse HTML files.
"""

import os
import re
import time
import random
from urllib.parse import urlparse
from bs4 import BeautifulSoup

class TheMatterParser:
    """
    A parser for The Matter news website that extracts article information,
    saves content to organized directories, and provides manual parsing capabilities.
    """
    
    def __init__(self, base_output_dir):
        """
        Initialize the parser with a base output directory for storing scraped content.
        
        Args:
            base_output_dir (str): Root directory where all scraped content will be saved
        """
        self.base_output_dir = base_output_dir

    def parse_listing(self, response):
        """
        Parse an article listing page to extract basic article information.
        
        Args:
            response: Scrapy response object containing the HTML of a listing page
            
        Returns:
            list: A list of dictionaries containing article titles, links, and dates
        """
        articles = response.css("div.post_wrapper")
        parsed_items = []

        for article in articles:
            # Extract article title
            title = article.css("div.post_header_title h5 a::text").get()
            # Extract article URL
            link = article.css("div.post_header_title h5 a::attr(href)").get()
            # Extract publication date
            date_text = article.css("div.post_detail.post_date span.post_info_date span::text").get()

            if title and link:
                parsed_items.append({
                    'title': title.strip(),
                    'link': link.strip(),
                    'date': date_text.replace("Posted On", "").strip() if date_text else ''
                })

        return parsed_items

    def parse_details(self, response, metadata):
        """
        Parse an article detail page to extract full content and save to files.
        
        Args:
            response: Scrapy response object containing the HTML of an article page
            metadata (dict): Article metadata containing title, link, and date
            
        Returns:
            dict: Parsed article information including save location
        """
        # Add random delay to avoid overwhelming the server
        time.sleep(1 + random.uniform(0.2, 0.4))

        full_html = response.text
        soup = BeautifulSoup(full_html, "html.parser")
        
        # Extract main content div
        content_div = soup.find("div", class_="post_content_wrapper")
        content = content_div.get_text(separator="\n", strip=True) if content_div else ""

        # Extract publication date from meta tags or fall back to listing date
        date = (
            response.css("meta[property='article:published_time']::attr(content)").get()
            or response.css("span.date::text").get()
            or metadata.get('date', '')
        ).strip()

        # Sanitize and format date string for folder name
        date_folder = date.replace('/', '-').replace(':', '-').replace(' ', '_') or 'unknown_date'

        # Create a slug from URL for file naming
        url_path = urlparse(metadata["link"]).path
        segments = url_path.strip("/").split("/")
        slug = segments[-2] if len(segments) >= 2 else segments[-1]

        # Construct full output directory path
        folder_path = os.path.join(self.base_output_dir, date_folder, slug)
        os.makedirs(folder_path, exist_ok=True)

        # Save full HTML
        with open(os.path.join(folder_path, f"{slug}.html"), "w", encoding="utf-8") as f:
            f.write(full_html)

        # Extract all reference links from the content
        ref_links = [a["href"] for a in content_div.find_all("a", href=True)] if content_div else []

        # Save metadata and content
        with open(os.path.join(folder_path, f"{slug}.txt"), "w", encoding="utf-8") as f:
            f.write(f"Title: {metadata['title']}\n")
            f.write(f"Date: {date}\n")
            f.write(f"Content:\n{content}\n")
            f.write(f"Ref link: {ref_links}\n")

        return {
        'title': metadata['title'],
        'date': date,
        'link': metadata['link'],
        'html_saved_as': folder_path
        }

    @staticmethod
    def parse_html(file_path):
        """
        Static method for manually parsing a saved MATTER news HTML file.
        Useful for offline processing of previously saved articles.
        
        Args:
            file_path (str): Path to the HTML file to parse
            
        Returns:
            dict: Parsed article information including title, date, content and reference links
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        # Extract article title
        title_tag = soup.find('h1')
        title = title_tag.get_text(strip=True) if title_tag else ''

        # Extract publication date
        date_tag = soup.find('span', class_='post_info_date')
        date = ''
        if date_tag:
            date_match = re.search(r'Posted On (.+)', date_tag.get_text())
            if date_match:
                date = date_match.group(1).strip()

        # Extract main content
        content_div = soup.find('div', class_='post_content_wrapper')
        content = content_div.get_text(separator='\n', strip=True) if content_div else ''

        # Extract all internal links
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if 'thematter.co' in href:
                links.append(href)

        return {
            'title': title,
            'date': date,
            'content': content,
            'ref_links': list(set(links))  # Return unique links only
        }