from Crawler import SpringNewsCrawler

if __name__ == '__main__':
    start_num = 856120
    last_num = 856140
    base_directory = r"C:\Users\saree\Desktop\Aitim\practical data\storage_1"  # Change to your desired directory

    crawler = SpringNewsCrawler(start_num, last_num, base_directory)
    crawler.run()