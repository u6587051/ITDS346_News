import requests
import os

def get_html(url, folder_number, count):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses
        
        # Set folder path to /root/newscoma@friday/data1-2tb/test_bkkbliz
        folder_path = os.path.join("/root/newscoma@friday/data1-2tb/test_bkkbliz", f"{folder_number}")
        os.makedirs(folder_path, exist_ok=True)
        
        # Save HTML content to a file
        file_path = os.path.join(folder_path, "page.html")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(response.text)
        
        print(f"{folder_number} HTML content saved, count={count}")
    except requests.exceptions.RequestException as e:
        print("Error fetching the page:", e)

start_index = 1164980
end_index = 1164990
c = 0 
for i in range(start_index, end_index + 1):
    url = f"https://www.bangkokbiznews.com/business/economic/{i}"
    c += 1
    get_html(url, i, c)
