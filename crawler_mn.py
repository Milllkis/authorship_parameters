import requests
from tqdm.auto import tqdm
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import pandas as pd
import random

session = requests.session()
ua = UserAgent()

def get_info_authors_page(page_number):
    # скачиваем страницу
    url = f'https://mirnov.ru/authors/l/{page_number}'
    req = session.get(url, headers={'User-Agent': ua.random})
    page = req.text
    soup = BeautifulSoup(page, 'html.parser')

    # делаем автора анонимным
    my_randoms = random.sample(range(1, 2249), 2240)
    name_code = 0

    # находим статьи на странице
    table = soup.find_all('table', {'id': 'authors'})

    # создаем словарь для хранения данных
    authors_data = {}

    # обработка
    rows = table[0].find_all('tr')[1:]  # Пропускаем первую строку с заголовками

    for row in rows:
        author_name = 'Автор ' + str(my_randoms[name_code])
        name_code += 1
        article_count = row.find_all('td')[2].text.strip()
        author_link = row.find('a')['href']

        if int(article_count) >= 270:
            authors_data[author_name] = author_link

    return authors_data


def get_info_one_author_page(author_href):
    url = f'https://mirnov.ru{author_href}'
    req = session.get(url, headers={'User-Agent': ua.random})
    page = req.text
    soup = BeautifulSoup(page, 'html.parser')

    # находим статьи на странице
    news = soup.find_all('div', {'id': 'artlist'})

    # создаем список для хранения данных
    news_links= []

    # обработка
    rows = news[0].find_all('p')

    for row in rows:
        news_link = row.find('a')['href']
        news_links.append(news_link)

    return news_links

def parse_one_article(link):
    url_one = f'https://mirnov.ru{link}'
    req = session.get(url_one, headers={'User-Agent': ua.random})
    page = req.text
    soup = BeautifulSoup(page, 'html.parser')

    title = str(soup.find('title'))[7:-8]
    category = link.split('/')[1]
    date = str(soup.find('time', {'itemprop':'dateline'}))[82:-7]

    t = ''
    paragraphs = soup.find_all('div', {'itemprop':'articleBody'}, 'p')
    for p in paragraphs:
        t += p.get_text()
    text = ' '.join(t.split('\n')[20:-3])

    return title, category, date, text

def run_all(n_pages):
    df = pd.DataFrame(columns=['Author', 'Category', 'Title', 'Text', 'Date', 'Link'])
    count = 0
    for page_number in tqdm(range(n_pages)):
        authors = get_info_authors_page(page_number)
        if authors:
            for name, link in authors.items():
                news_links = get_info_one_author_page(link)
                for news in news_links:
                    title, category, date, text = parse_one_article(news)
                    if len(text.split()) > 1000:
                        link = 'https://mirnov.ru' + news
                        df.loc[count] = [name, category, title[:-15], text, date, link]
                        count += 1
    return df

data_mn = run_all(27)
data_mn.to_csv('news_mn.csv', index=False)