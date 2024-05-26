import requests
from tqdm.auto import tqdm
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import pandas as pd
import random
from collections import Counter

session = requests.session()
ua = UserAgent()

def get_info_authors_page(url):

    # скачиваем страницу
    req = session.get(url, headers={'User-Agent': ua.random})
    page = req.text
    soup = BeautifulSoup(page, 'html.parser')

    # делаем автора анонимным
    my_randoms = random.sample(range(2250, 4501), 2240)
    name_code = 0

    # создаем словарь для хранения данных
    authors_data = {}

    # обработка
    authors = soup.find_all('article', {'class':'author-preview'})

    for author in authors:
        name = 'Автор ' + str(my_randoms[name_code])
        name_code += 1
        link = author.find('a')['href']
        publications = int(author.find('span', {'class':'author-preview__publications-text'}).text[12:])

        if int(publications) >= 1000:
            authors_data[name] = link

    return authors_data

def get_author_publications(author_url):

    # скачиваем страницу
    req = session.get(author_url, headers={'User-Agent': ua.random})
    page = req.text
    soup = BeautifulSoup(page, 'html.parser')

    # какой период времени
    years_list = soup.find_all('a', {'class':'news-listing__pagination-link news-listing__pagination-link_year'})
    years = [year['href'] for year in years_list]

    publication_links = []

    for yl in years:
        url = f'https://www.mk.ru{yl}'
        req = session.get(url, headers={'User-Agent': ua.random})
        page = req.text
        soup = BeautifulSoup(page, 'html.parser')

        pages_list = soup.find_all('a', {'class':'news-listing__pagination-link'})
        pages = [page['href'] for page in pages_list]
        pages = pages[len(years):]

        if pages:
            for page in pages:
                url = f'https://www.mk.ru{page}'
                req = session.get(url, headers={'User-Agent': ua.random})
                page = req.text
                soup = BeautifulSoup(page, 'html.parser')

                links_p = soup.find_all('article', {'class':'article-preview article-preview_in-story'})

                for article in links_p:
                    link = article.find('a', {'class':'article-preview__content'})['href']
                    publication_links.append(link)

    return publication_links

def parse_one_article(url):
    req = session.get(url, headers={'User-Agent': ua.random})
    page = req.text
    soup = BeautifulSoup(page, 'html.parser')

    title = str(soup.find('title').text)[:-5]
    category = url.split('/')[3]
    date = str(soup.find('time', {'class':'meta__text'}))

    text = ''
    paragraphs = soup.find_all('div', {'itemprop':'articleBody'}, 'p')
    for p in paragraphs:
        text += p.text

    return title, category, date, text

def run_all(page):
    df = pd.DataFrame(columns=['Author', 'Category', 'Title', 'Text', 'Date', 'Link'])
    count = 0
    authors = get_info_authors_page(page)
    for name, link in tqdm(authors.items()):

        try:
            news_links = get_author_publications(link)
            cats = []
            for l in news_links:
                cats.append(l.split('/')[3])
            d_cats = Counter(cats)
            counts = sum(1 for count in d_cats.values() if count >= 200)
            if counts >= 3:
                for news in news_links:
                    title, category, date, text = parse_one_article(news)
                    text = text.replace('\n', ' ').strip()
                    if len(text.split()) > 1000:
                        df.loc[count] = [name, category, title, text, date, news]
                        count += 1
        except:
            continue
    return df

data_mk = run_all('https://www.mk.ru/authors/')
data_mk.to_csv('news_mk.csv', index=False)