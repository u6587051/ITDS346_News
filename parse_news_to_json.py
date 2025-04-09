import os
import json
from bs4 import BeautifulSoup

def extract_news_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract title
    title = soup.find("meta", property="og:title")
    title = title.get("content", "").strip() if title else (soup.title.string.strip() if soup.title else "No Title")
    
    # Extract date
    date = soup.find("meta", property="article:published_time")
    date = date.get("content", "").strip() if date else "No Date Found"
    
    # Extract URL
    url = soup.find("meta", property="og:url")
    url = url.get("content", "").strip() if url else "No URL Found"
    
    
    return {
        "title": title,
        "date": date,
        "url": url
    }

# reach everyfolder then parse and save 
def process_folder(root_folder):
    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename == "index.html":
                full_path = os.path.join(dirpath, filename)
                with open(full_path, "r", encoding="utf-8") as f:
                    html_content = f.read()

                data = extract_news_data(html_content)

                # save json
                json_path = os.path.join(dirpath, "data.json")
                with open(json_path, "w", encoding="utf-8") as jf:
                    json.dump(data, jf, ensure_ascii=False, indent=2)
                print(f"✅ Parsed and saved JSON for: {full_path}")


if __name__ == "__main__":
    root_folder = "storage/news"
    process_folder(root_folder)
