import os
from urllib.parse import urlparse
import json  # You might not need this anymore, but keep it for now
from scrapy.selector import Selector  # Import Selector
from bs4 import BeautifulSoup

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
        """บันทึกไฟล์ HTML และ Text"""  # Changed comment
        full_html = response.body.decode('utf-8')
        folder_path = os.path.join(self.base_directory, folder_name)

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        html_filename = os.path.join(folder_path, "index.html")
        text_filename = os.path.join(folder_path, "data.txt")  # Changed filename

        with open(html_filename, 'w', encoding='utf-8') as file:
            file.write(full_html)

        # Save data as text instead of JSON
        with open(text_filename, 'w', encoding='utf-8') as file:
            file.write(f"Title: {data.get('title', 'No Title')}\n")
            file.write(f"Description: {data.get('description','No Description')}\n")
            file.write(f"Content: {data.get('content')}\n")
            file.write(f"Date: {data.get('date', 'No Date')}\n")
            file.write(f"URL: {data.get('url', 'No URL')}\n")
            file.write(f"Original URL: {data.get('original_url', 'No Original URL')}\n")
            file.write(f"Redirected URL: {data.get('redirected_url', 'No Redirected URL')}\n")
            file.write(f"Folder Name: {data.get('folder_name', 'No Folder Name')}\n")
            # You can add more data here as needed

        return {
            'url': response.url,
            'html_saved_as': html_filename,
            'text_saved_as': text_filename,  # Changed key name
        }

   
    def extract_news_data_selectors(self, response):

        # Extract title
        title_selector = response.css("meta[property='og:title']::attr(content)")
        title = title_selector.get("").strip() if title_selector else (
            response.css("title::text").get("").strip() if response.css("title::text").get() else "No Title"
        )

        # Extract description
        description_selector = response.css("meta[property='og:description']::attr(content)")
        description = description_selector.get("").strip() if description_selector else (
            response.css("title::text").get("").strip() if response.css("title::text").get() else "No Description"
        )

        # ✅ Extract content using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        news_content = []
        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 30:
                news_content.append(text)
        full_article = "\n".join(news_content)

        # Extract date
        date_selector = response.css("meta[property='article:published_time']::attr(content)")
        date = date_selector.get("").strip() if date_selector else "No Date Found"

        # Extract URL
        url_selector = response.css("meta[property='og:url']::attr(content)")
        url = url_selector.get("").strip() if url_selector else "No URL Found"

        return {
            "title": title,
            "description": description,
            "content": full_article,
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