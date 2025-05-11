from Crawler import SpringNewsCrawler

if __name__ == '__main__':
    start_num = 857630
    last_num = 857640
    base_directory = r"C:\Users\saree\Desktop\Aitim\practical data\Springnews_storage"  # Change to your desired directory
    
    crawler = SpringNewsCrawler(start_num, last_num, base_directory)
    crawler.run()