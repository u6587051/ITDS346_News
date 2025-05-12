import os  # For interacting with the operating system (e.g., creating directories)
from urllib.parse import urlparse  # For parsing URLs
import json  # Potentially for JSON handling (may not be strictly needed in this version)
from scrapy.selector import Selector  # Scrapy's CSS/XPath selector (if you want to use it directly)
from bs4 import BeautifulSoup  # For parsing HTML

class SpringNewsParser:
    """
    This class is responsible for parsing the HTML content of a news article
    and saving the extracted data to files.
    """

    def __init__(self, base_directory):
        """
        Initializes the parser with the base directory where data will be saved.

        Args:
            base_directory (str): The directory where the output files will be stored.
        """
        self.base_directory = base_directory

    def is_redirected_to_home(self, redirected_url):
        """
        Checks if a given URL has been redirected to the Spring News homepage.
        This is often used to identify articles that don't exist or have been removed.

        Args:
            redirected_url (str): The URL that the crawler ended up at after any redirects.

        Returns:
            bool: True if the URL is the homepage, False otherwise.
        """
        home_url = "https://www.springnews.co.th/"
        parsed_url = urlparse(redirected_url)
        # Normalize URLs for comparison (remove trailing slashes, etc.)
        return parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path == home_url

    def get_folder_structure(self, url, page_id):
        """
        Generates the folder structure where the HTML and text data for a news article
        will be saved.  It attempts to mirror the URL structure if possible.

        Args:
            url (str): The original URL of the news article.
            page_id (int):  The unique page ID of the article.

        Returns:
            str: The full path to the folder where the data should be saved.
        """

        # Create the "Spring news" directory at the base if it doesn't exist
        spring_news_dir = os.path.join(self.base_directory, "Spring news")
        if not os.path.exists(spring_news_dir):
            os.makedirs(spring_news_dir)

        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')  # Split the URL path into parts
        if len(path_parts) > 1:
            folder_path = os.path.join("news", *path_parts)  # Create a folder structure like "news/section/subsection/..."
        else:
            folder_path = str(page_id)  # If the URL is very simple, just use the page ID as the folder name

        return os.path.join(spring_news_dir, folder_path)  # Combine the base directory and the generated folder path

    def save_html_and_json(self, response, folder_name, data):
        """
        Saves the raw HTML of the response and the extracted news data to separate files.

        Args:
            response (scrapy.http.Response): The Scrapy response object (containing the HTML).
            folder_name (str): The name of the folder where the files should be saved.
            data (dict): A dictionary containing the extracted news data.

        Returns:
            dict: A dictionary containing information about where the files were saved.
        """
        full_html = response.body.decode('utf-8')  # Decode the HTML content
        folder_path = os.path.join(self.base_directory, folder_name)  # Create the full folder path

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)  # Create the folder if it doesn't exist

        html_filename = os.path.join(folder_path, "index.html")  # Name for the HTML file
        text_filename = os.path.join(folder_path, "data.txt")   # Name for the text file

        with open(html_filename, 'w', encoding='utf-8') as file:
            file.write(full_html)  # Save the raw HTML

        # Save extracted data to a text file
        with open(text_filename, 'w', encoding='utf-8') as file:
            file.write(f"Title: {data.get('title', 'No Title')}\n")
            file.write(f"Description: {data.get('description','No Description')}\n")
            file.write(f"Content: {data.get('content')}\n")
            file.write(f"Date: {data.get('date', 'No Date')}\n")
            file.write(f"URL: {data.get('url', 'No URL')}\n")
            file.write(f"Original URL: {data.get('original_url', 'No Original URL')}\n")
            file.write(f"Redirected URL: {data.get('redirected_url', 'No Redirected URL')}\n")
            file.write(f"Folder Name: {data.get('folder_name', 'No Folder Name')}\n")

        return {  # Return information about where the files were saved
            'url': response.url,
            'html_saved_as': html_filename,
            'text_saved_as': text_filename,
        }

    def extract_news_data_selectors(self, response):
        """
        Extracts news article data (title, description, content, date, URL)
        from the HTML response using Scrapy CSS selectors and BeautifulSoup.

        Args:
            response (scrapy.http.Response): The Scrapy response object.

        Returns:
            dict: A dictionary containing the extracted news data.
        """

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

        #  Extract content using BeautifulSoup (more robust for complex HTML)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        news_content = []
        for p in paragraphs:
            text = p.get_text(strip=True)  # Get text, removing extra whitespace
            if len(text) > 30:  # Only include paragraphs with significant content
                news_content.append(text)
        full_article = "\n".join(news_content)  # Join the paragraphs with newline characters

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
        """
        Orchestrates the parsing of the HTML content and saving of the extracted data.

        Args:
            response (scrapy.http.Response): The Scrapy response object.
            folder_name (str): The name of the folder to save data in.
            page_id (int): The unique page ID of the article.
            redirected_url (str): The actual URL the crawler ended up at.

        Returns:
            dict: The extracted data.
        """

        all_text = response.xpath("//text()").getall()  # Get all text from the HTML (for potential full-text analysis)
        cleaned_text = " ".join([t.strip() for t in all_text if t.strip()])  # Clean the text (remove extra spaces)

        # Extract news data using Scrapy Selectors and BeautifulSoup
        news_data = self.extract_news_data_selectors(response)

        # Prepare the data to be saved
        data_to_save = {
                'original_url': f'https://www.springnews.co.th/news/{page_id}',
                'redirected_url': redirected_url,
                'folder_name': folder_name,
            }

        if news_data:
            data_to_save.update(news_data)  # Merge the extracted data

        self.save_html_and_json(response, folder_name, data_to_save)

        return data_to_save