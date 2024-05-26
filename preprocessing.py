import pandas as pd
import os
import re
import numpy as np
from bs4 import BeautifulSoup
import time
from datetime import datetime

df_mn = pd.read_csv('news_mn.csv')
df_mk = pd.read_csv('news_mk.csv')


# Во-первых, мы уберем любое цитирование из текстов и проверим, осталось ли там более 1000 слов.
df_mn['Text'] = df_mn['Text'].apply(lambda x: re.sub(r'«.+?»','', str(x)))
df_mk['Text'] = df_mk['Text'].apply(lambda x: re.sub(r'«.+?»','', str(x)))

df_mn['Text'] = df_mn['Text'].apply(lambda x: re.sub(r'“.+?”','', str(x)))
df_mk['Text'] = df_mk['Text'].apply(lambda x: re.sub(r'“.+?”','', str(x)))

df_mn['Word_count'] = df_mn['Text'].apply(lambda x: len(x.split()))
df_mk['Word_count'] = df_mk['Text'].apply(lambda x: len(x.split()))

df_mn = df_mn[df_mn.Word_count >= 1000]
df_mk = df_mk[df_mk.Word_count >= 1000]


# Во-вторых, мы почистим весь датафрейм от лишних пробелов и переносов строк. В тех случаях, когда в текст статьи попал заголовок мы его уберем. Также убедимся, что в наших данных нет дубликатов.
df_mn.Title = df_mn.Title.str.replace(r'\s+', ' ', regex=True)
df_mn.Title = df_mn.Title.str.strip()
df_mn.Title = df_mn.Title.str.capitalize()
df_mn.Text = df_mn.Text.str.replace(r'\s+', ' ', regex=True)
df_mn.Text = df_mn.Text.str.strip()
df_mn.Text = df_mn.Text.str.replace('\r', '')
df_mn.Text = df_mn.Text.str.replace('\xad', '')
df_mn.Text = df_mn.Text.str.replace('\u00ad', '')
for i, row in df_mn.iterrows():
    if str(row.Title) == row.Text[:len(str(row.Title))]:
        df_mn.loc[i,'Text'] = str(row.Text[len(str(row.Title)):]).strip()

df_mn = df_mn.drop_duplicates(subset=['Author', 'Title'])

df_mk.Title = df_mk.Title.str.replace(r'\s+', ' ', regex=True)
df_mk.Title = df_mk.Title.str.strip()
df_mk.Title = df_mk.Title.str.capitalize()
df_mk.Text = df_mk.Text.str.replace(r'\s+', ' ', regex=True)
df_mk.Text = df_mk.Text.str.strip()
df_mn.Text = df_mn.Text.str.replace('&mdash;', '—')
df_mn.Text = df_mn.Text.str.replace('&ndash;', '–')
for i, row in df_mk.iterrows():
    if '<' in str(row.Date):
        df_mk.loc[i,'Date'] = str(row.Date).split('>')[1].split()[0]

df_mk = df_mk.drop_duplicates(subset=['Author', 'Title'])


#мы не будем рассматривать авторов, у которых менее 100 статей. Мы считаем, что в противном случае данных может оказаться слишком мало.
df2 = df_mn.groupby('Author')['Author'].agg(count='count')
df2 = df2.loc[df2['count'] >= 100].reset_index()
df_mn = df_mn[df_mn['Author'].isin(list(df2['Author']))] #оставляем только авторов из списка выше

df2 = df_mk.groupby('Author')['Author'].agg(count='count')
df2 = df2.loc[df2['count'] >= 300].reset_index()
df_mk = df_mk[df_mk['Author'].isin(list(df2['Author']))] #оставляем только авторов из списка выше


#В-третьих, категории должны быть написаны кириллицей для удобства восприятия, а также мы предлагаем сделать небольшую реорганизацию и улучшить деление на категории:
df_mn.loc[df_mn['Category']=='recipes', ['Rubric']] = 'Здоровье и спорт'
df_mn.loc[df_mn['Category']=='zdorove', ['Rubric']] = 'Здоровье и спорт'
df_mn.loc[df_mn['Category']=='za-kulisami-sporta', ['Rubric']] = 'Здоровье и спорт'
df_mn.loc[df_mn['Category']=='kriminalnye-novosti', ['Rubric']] = 'Происшествия'
df_mn.loc[df_mn['Category']=='kriminalnye-novosti-chrezvychainye-proisshestvija', ['Rubric']] = 'Происшествия'
df_mn.loc[df_mn['Category']=='nauka-i-tekhnika ', ['Rubric']] = 'Это интересно'
df_mn.loc[df_mn['Category']=='rubriki-novostey', ['Rubric']] = 'Это интересно'
df_mn.loc[df_mn['Category']=='politika', ['Rubric']] = 'Политика и Экономика'
df_mn.loc[df_mn['Category']=='ekonomika', ['Rubric']] = 'Политика и Экономика'
df_mn.loc[df_mn['Category']=='otkroveniya-zvezd', ['Rubric']] = 'Культура'
df_mn.loc[df_mn['Category']=='kultura', ['Rubric']] = 'Культура'
df_mn.loc[df_mn['Category']=='arhiv-mn', ['Rubric']] = 'Архивные записи'
df_mn.loc[df_mn['Category']=='obshchestvo', ['Rubric']] = 'Общество'

df_mk.loc[df_mk['Category']=='nasha-moskva', ['Rubric']] = 'Москва и область'
df_mk.loc[df_mk['Category']=='zloba-dnya', ['Rubric']] = 'Происшествия'
df_mk.loc[df_mk['Category']=='auto', ['Rubric']] = 'Общество'
df_mk.loc[df_mk['Category']=='science', ['Rubric']] = 'Наука'
df_mk.loc[df_mk['Category']=='culture', ['Rubric']] = 'Культура'
df_mk.loc[df_mk['Category']=='mosobl', ['Rubric']] = 'Москва и область'
df_mk.loc[df_mk['Category']=='sport', ['Rubric']] = 'Спорт'
df_mk.loc[df_mk['Category']=='moscow', ['Rubric']] = 'Москва и область'
df_mk.loc[df_mk['Category']=='old', ['Rubric']] = 'Архивные записи'
df_mk.loc[df_mk['Category']=='incident', ['Rubric']] = 'Происшествия'
df_mk.loc[df_mk['Category']=='economics', ['Rubric']] = 'Экономика'
df_mk.loc[df_mk['Category']=='politics', ['Rubric']] = 'Политика'
df_mk.loc[df_mk['Category']=='editions', ['Rubric']] = 'От редакции'
df_mk.loc[df_mk['Category']=='social', ['Rubric']] = 'Общество'
df_mk.loc[df_mk['Category']=='articles', ['Rubric']] = 'Общество'
df_mk.loc[df_mk['Category']=='daily', ['Rubric']] = 'Общество'

df_mn.drop(['Category'], axis=1)
df_mk.drop(['Category'], axis=1)

df = pd.concat([df_mn,df_mk])
df = df.dropna()
df.to_csv('news_df_final.csv')

#Оставляем только нужных авторов и ограничиваем выборку
for author in df['Author'].unique():
    start = 0
    count = 0
    rubrics = len(df[df.Author == author]['Rubric'].unique())
    for i in range(rubrics):
        if df[df.Author == author].groupby('Rubric')['Rubric'].agg(count='count')['count'][i] >= 29:
            count += 1
    if count >= 3:
        print(author)