import os
import re
import time
import random
from urllib.parse import urlparse
from bs4 import BeautifulSoup

class TheMatterParser:
    def __init__(self, base_output_dir):
        self.base_output_dir = base_output_dir

    def parse_listing(self, response):
        # Parse listing page to extract articles
        articles = response.css("div.post_wrapper")
        parsed_items = []

        for article in articles:
            title = article.css("div.post_header_title h5 a::text").get()
            link = article.css("div.post_header_title h5 a::attr(href)").get()
            date_text = article.css("div.post_detail.post_date span.post_info_date span::text").get()

            if title and link:
                parsed_items.append({
                    'title': title.strip(),
                    'link': link.strip(),
                    'date': date_text.replace("Posted On", "").strip() if date_text else ''
                })

        return parsed_items

    def parse_details(self, response, metadata):
        # Delay to avoid aggressive crawling
        time.sleep(1 + random.uniform(0.2, 0.4))

        full_html = response.text
        soup = BeautifulSoup(full_html, "html.parser")
        content_div = soup.find("div", class_="post_content_wrapper")
        content = content_div.get_text(separator="\n", strip=True) if content_div else ""

        date = (
            response.css("meta[property='article:published_time']::attr(content)").get()
            or response.css("span.date::text").get(default=metadata['date'])
        ).strip()

        url_path = urlparse(metadata["link"]).path
        segments = url_path.strip("/").split("/")
        slug = segments[-2] if len(segments) >= 2 else segments[-1]

        folder_path = os.path.join(self.base_output_dir, slug)
        os.makedirs(folder_path, exist_ok=True)

        with open(os.path.join(folder_path, f"{slug}.html"), "w", encoding="utf-8") as f:
            f.write(full_html)

        ref_links = [a["href"] for a in content_div.find_all("a", href=True)] if content_div else []

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

    def parse_html(file_path):
        # Parse stored HTML file manually (not used by crawler)
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        title_tag = soup.find('h1')
        title = title_tag.get_text(strip=True) if title_tag else ''

        date_tag = soup.find('span', class_='post_info_date')
        date = ''
        if date_tag:
            date_match = re.search(r'Posted On (.+)', date_tag.get_text())
            if date_match:
                date = date_match.group(1).strip()

        content_div = soup.find('div', class_='post_content_wrapper')
        content = content_div.get_text(separator='\n', strip=True) if content_div else ''

        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if 'thematter.co' in href or 'cnbc.com' in href or 'thaipbs.or.th' in href:
                links.append(href)

        return {
            'title': title,
            'date': date,
            'content': content,
            'ref_links': list(set(links))
        }