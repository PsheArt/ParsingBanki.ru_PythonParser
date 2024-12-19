import numpy as np
import csv
import pandas as pd
import numpy as np
import requests
import json
import xlsxwriter
import re
from pprint import pprint
from random import choice
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup as bs
desktop_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0']
def random_headers():
    return {'User-Agent': choice(desktop_agents),'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}    
print('Введите кол-во страниц: ')
page_c = int(input())
file_json = 'file.json'
file_xlsx = 'file.xlsx'
def soup_get(url):
    response = requests.get(url,headers=random_headers())
    if response.status_code == 200 or response.status_code == 429:
        soup = bs(response.text, features = 'html.parser')
    else:
        soup=None
    return soup
def comment_crawl(pages_count):
    urls = []
    site = 'https://www.banki.ru/services/responses/bank/sberbank/product/creditcards/?is_countable=on&page={page}&isMobile=0'
    for page_n in range(1, 1 + pages_count):
        print('page:{}'.format(page_n))
        page_url = site.format(page=page_n)
        soup = soup_get(page_url)
        if soup is None:
            break
        for tag in soup.select('.header-h3'):
            href = tag.attrs['href']
            url = 'https://www.banki.ru{}'.format(href)
            urls.append(url)
    return urls
def comment_parse(urls):
    data = []
    for url in urls:
        html = soup_get(url)
        if html is None:
            break
        title = html.select_one('.header-h0').text.strip()
        #rating = [p.get_text().strip() for p in html.find_all("span",{"class":"rating-grade"})]
        rating = html.select_one('.rating-grade').text.strip()
        bank = html.select_one('.display-inline').text.strip()
        about = html.select_one('.article-text').text.strip()
        date = html.find('time')['datetime']
        item = {
                'title': title,
                'rating': rating,
                'bank':bank,
                'about':about,
                'date':date,
                }
        data.append(item)
    return data
def to_json(filename, data):
    with open(filename, 'w',encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
def to_xlsx(filename, data):
    if not len(data):
        return None
    with xlsxwriter.Workbook(filename) as workbook:
        wshe = workbook.add_worksheet()
        bold = workbook.add_format({'bold': True})
        headers = ['Заголовок отзыва', 'Оценка', 'Дата отзыва', 'Банк', 'Содержание отзыва']
        for col, h in enumerate(headers):
            wshe.write_string(0, col, h, cell_format=bold)
            for row, item in enumerate(data, start=1):
                wshe.write_string(row, 0, item['title'])
                wshe.write_string(row, 1, item['rating'])
                wshe.write_string(row, 2, item['date'])
                wshe.write_string(row, 3, item['bank'])
                wshe.write_string(row, 4, item['about'])
urls = comment_crawl(page_c)
print ('\n'.join(urls))
data = comment_parse(urls)
pprint(data)
to_json(file_json, data)
to_xlsx(file_xlsx, data)
