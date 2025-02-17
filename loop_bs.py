import requests
from bs4 import BeautifulSoup

data = requests.get("https://thestandard.co/category/news/business/")
soup = BeautifulSoup(data.text, 'lxml')
# print(soup)
news = soup.find('div',{'class': 'news-item'})

title = news.find('h3',{'class': 'news-title'})
news_title = title.find('a').text.strip()
print(news_title)

date = news.find('div',{'class': 'date'}).text.strip()
print(date)