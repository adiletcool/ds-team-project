from bs4 import BeautifulSoup
import requests
from datetime import datetime
from lxml.html import fromstring

url = 'https://www.interfax.ru/news/'


def get_news(date: datetime):
    # list of news titles
    main_page = f'{url}{date.year}/{date.month}/{date.day}'
    soup = BeautifulSoup(requests.get(main_page).content, 'html.parser')

    # Определяем число страниц с новостями за день (обычно три)
    n_pages = int(soup.find('div', {'class': 'pages'}).getText()[-2])

    # Проходим по всем страницам и достаем все новости
    all_news = []
    for i in range(1, n_pages + 1):
        news_soup = BeautifulSoup(requests.get(f'{main_page}/all/page_{str(i)}').content, 'html.parser')
        news = news_soup.find('div', {'class': 'an'}).findAll('div')
        all_news.extend([nw for nw in news if len("" if not nw.get('data-id') else nw.get('data-id')) > 0])

    # Сохраняем в список из словарей
    # to-do: add rubrics [business, world, russia, moscow] по сути нет только culture
    result = [
        dict(
            time=n.find('span').text,
            date=date.strftime('%d.%m.%Y'),
            title=n.find('a').text,
            href=n.find('a').get('href')
        )
        for n in all_news
    ]
    res_filtered = [i for i in result if any(r in i['href'] for r in ['russia', 'world', 'business', 'moscow'])]

    return res_filtered


def get_content(href):
    soup = BeautifulSoup(requests.get(f'https://www.interfax.ru{href}').content, 'html.parser')
    article = soup.find('article', {'itemprop': 'articleBody'})
    article_text = [i.getText() for i in article.findAll('p')]

    title = fromstring(requests.get(f'https://www.interfax.ru{href}').content).findtext('.//title')
    time = soup.find('a', {'class': 'time'}).getText().strip()[:5]

    return dict(content=article_text, title=title, time=time)


if __name__ == '__main__':
    print(get_news(datetime.today()))
