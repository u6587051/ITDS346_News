from Crawler import SpringNewsCrawler  # Import the SpringNewsCrawler class

if __name__ == '__main__':
    start_num = 857630  # The starting page number for crawling
    last_num = 857640   # The last page number for crawling
    base_directory = "../newscoma_output"  # The base directory where the output will be saved

    crawler = SpringNewsCrawler(start_num, last_num, base_directory)  # Create an instance of the crawler
    crawler.run()  # Start the crawling process