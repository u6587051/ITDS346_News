import scrapy
import os
from urllib.parse import urlparse


class SpringSpider(scrapy.Spider):
    name = 'springSpider'
    start_num = 856120
    last_num = 856140

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }

    start_urls = []


    def __init__(self):
        for i in range(self.start_num, self.last_num + 1):
            self.start_urls.append((f'https://www.springnews.co.th/news/{i}', i))

    def start_requests(self):
        """เริ่ม request และส่ง page_id ไปด้วย"""
        for url, page_id in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={'page_id': page_id})

    def parse(self, response):
        """เก็บ URL ที่ redirect แล้ว และบันทึกไฟล์ใน news/{category}/{subcategory}/{page_id}/"""
        page_id = response.meta['page_id']
        redirected_url = response.url  # URL ที่ redirect ไปแล้ว

        if self.is_redirected_to_home(redirected_url):
            self.logger.warning(f"Skipping URL {redirected_url} (Redirected to homepage)")
            return  # หยุดการดึงข้อมูล

        folder_name = self.get_folder_structure(redirected_url, page_id)

        all_text = response.xpath("//text()").getall()
        cleaned_text = " ".join([t.strip() for t in all_text if t.strip()])

        yield from self.save_html(response, folder_name)

        yield {
            'original_url': f'https://www.springnews.co.th/news/{page_id}',
            'redirected_url': redirected_url,  # เก็บ URL ใหม่
            'folder_name': folder_name,  # ใช้ URL ที่ Redirect เป็นชื่อโฟลเดอร์
            'text_content': cleaned_text,
        }

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
            folder_path = os.path.join("news", *path_parts)  #example news/category/subcategory/page_id
        else:
            folder_path = os.path.join("news", str(page_id))  #example news/856130 (ถ้าไม่มีหมวดหมู่)

        return folder_path

    def save_html(self, response, folder_name):
        """บันทึกไฟล์ HTML"""
        full_html = response.body.decode('utf-8')

        base_directory = r"C:\Users\saree\Desktop\Aitim\practical data\storage"
        folder_path = os.path.join(base_directory, folder_name)

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        filename = os.path.join(folder_path, "index.html")

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(full_html)

        yield {
            'url': response.url,
            'html_saved_as': filename,
        }
