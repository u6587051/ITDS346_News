from Crawler import SpringNewsCrawler  # Import the SpringNewsCrawler class

if __name__ == '__main__':
    start_num = 857630
    last_num = 857640
    base_directory = "../newscoma_output"  # Change to your desired directory
    
    crawler = SpringNewsCrawler(start_num, last_num, base_directory)
    crawler.run()
