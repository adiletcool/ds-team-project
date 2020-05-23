from bs4 import BeautifulSoup
import requests
from urllib.parse import urlencode
from datetime import datetime, timedelta
from quotes.ricom.config import mfd_tickers_id
from lxml.html import fromstring

base_url = 'http://mfd.ru/news/company/view/?'


def mfd_get_news(date: datetime, company: str, period: int = 0):

    params = urlencode([('id', mfd_tickers_id.get(company)),
                        ('from', date.strftime('%d.%m.%Y')),
                        ('to', (date + timedelta(days=period)).strftime('%d.%m.%Y'))])

    soup = BeautifulSoup(requests.get(base_url + params).content, 'html.parser')

    table = soup.find('table', {'id': 'issuerNewsList'})

    if table is not None:
        rows = table.findAll('tr')
        res = [dict(time=n.find('td').text.split(', ')[-1].strip(),
                    date=n.find('td').text.split(', ')[0].strip(),
                    title=n.find('a').text.strip(),
                    href=n.find('a').get('href')) for n in rows]
    else:
        return []  # если не было новостей

    return res


def mfd_get_content(href: str):  # {'content': ..., 'title': ..., 'time': ...}
    req = requests.get(f'http://mfd.ru{href}').content
    soup = BeautifulSoup(req, 'html.parser')
    article = soup.find('div', {'class': 'm-content'})
    article_text = [i.getText() for i in article.findAll('p')]

    title = fromstring(req).findtext('.//title').split(' |')[0]
    time = soup.find('span', {'class': 'mfd-content-date'}).text

    return dict(content=article_text, title=title, time=time)


if __name__ == '__main__':
    # from pprint import pprint as pp
    # pp(get_company_news(datetime(2020, 5, 6), list(mfd_tickers_id.keys())[0]))
    soup1 = mfd_get_content('/news/view/?id=2359964&companyId=1')
