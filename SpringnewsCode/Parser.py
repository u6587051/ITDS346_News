import os
from urllib.parse import urlparse
import json
from scrapy.selector import Selector  # Import Selector

class SpringNewsParser:
    def __init__(self, base_directory):
        self.base_directory = base_directory

    def is_redirected_to_home(self, redirected_url):
        """ตรวจสอบว่า URL ที่ Redirect ไปคือหน้าแรกหรือไม่"""
        home_url = "https://www.springnews.co.th/"
        parsed_url = urlparse(redirected_url)
        return parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path == home_url

    def get_folder_structure(self, url, page_id):
        """สร้างชื่อโฟลเดอร์ให้ตรงกับโครงสร้าง URL"""
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')
        if len(path_parts) > 1:
            folder_path = os.path.join("news", *path_parts)
        else:
            folder_path = os.path.join("news", str(page_id))
        return folder_path

    def save_html_and_json(self, response, folder_name, data):
        """บันทึกไฟล์ HTML และ JSON"""
        full_html = response.body.decode('utf-8')
        folder_path = os.path.join(self.base_directory, folder_name)

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        html_filename = os.path.join(folder_path, "index.html")
        json_filename = os.path.join(folder_path, "data.json")

        with open(html_filename, 'w', encoding='utf-8') as file:
            file.write(full_html)

        with open(json_filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        return {
            'url': response.url,
            'html_saved_as': html_filename,
            'json_saved_as': json_filename,
        }

    def extract_news_data_selectors(self, response):
        """Extracts title, date, and URL from HTML using Scrapy Selectors."""

        # Extract title
        title_selector = response.css("meta[property='og:title']::attr(content)")
        title = title_selector.get("").strip() if title_selector else (response.css("title::text").get("").strip() if response.css("title::text").get() else "No Title")

        # Extract date
        date_selector = response.css("meta[property='article:published_time']::attr(content)")
        date = date_selector.get("").strip() if date_selector else "No Date Found"

        # Extract URL
        url_selector = response.css("meta[property='og:url']::attr(content)")
        url = url_selector.get("").strip() if url_selector else "No URL Found"

        return {
            "title": title,
            "date": date,
            "url": url
        }

    def parse_and_save(self, response, folder_name, page_id, redirected_url):
        """ทำการ parse ข้อมูลและบันทึกไฟล์"""

        all_text = response.xpath("//text()").getall()
        cleaned_text = " ".join([t.strip() for t in all_text if t.strip()])

        # Extract news data using Scrapy Selectors
        news_data = self.extract_news_data_selectors(response)

        data_to_save = {
            'original_url': f'https://www.springnews.co.th/news/{page_id}',
            'redirected_url': redirected_url,
            'folder_name': folder_name,
        }

        if news_data:
            data_to_save.update(news_data)  # Merge the extracted data

        self.save_html_and_json(response, folder_name, data_to_save)

        return data_to_save