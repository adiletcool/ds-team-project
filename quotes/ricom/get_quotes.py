import math
import pandas as pd
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import urlretrieve
from quotes.ricom.config import tickers_id, tfs


class Quotes:
    def __init__(self):
        self.base_url = 'https://www.ricom.ru/getChartCSV/?'
        self.tf = None
        self.ticker = None
        self.start_date = None
        self.end_date = None
        self.file = None
        self.file_tf = None

    def _download(self, ticker, start_date: datetime, end_date: datetime):
        if (self.ticker != ticker) or (self.start_date != start_date) or (self.end_date != end_date):
            self.tf = '1 мин.'
            self.ticker = ticker
            self.start_date = start_date
            self.end_date = end_date

            params = urlencode([
                ('export', 'True'),
                ('paper_id', tickers_id[ticker]),
                ('index_id', '-1'),
                ('period_type', 'day'),
                ('minDT', f'{int(start_date.timestamp() * 1e3)}'),
                ('maxDT', f'{int(end_date.timestamp() * 1e3)}')
            ])
            url = self.base_url + params

            urlretrieve(url, 'quotes.xls')
            file = pd.ExcelFile('quotes.xls').parse()
            file.columns = ['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']
            file = file.drop('VOLUME', axis=1)
            self.file = file
            return file
        else:
            return self.file

    def _change_tf(self, tf: str):
        if self.tf != tf:
            self.tf = tf
            columns = ['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE']
            n = tfs[tf]
            self.file_tf = pd.DataFrame(columns=columns)

            for i in range(math.ceil(len(self.file) / n)):
                res = []
                start = (n * i)
                end = (n * (i + 1)) if (n * (i + 1)) < len(self.file) else len(self.file)
                fd = self.file.iloc[start:end].to_dict()
                res.append(fd['DATE'][end - 1])
                res.append(fd['OPEN'][start])
                res.append(max([fd['LOW'][i] for i in range(start, end)]))
                res.append(min([fd['HIGH'][i] for i in range(start, end)]))
                res.append(fd['CLOSE'][end - 1])
                self.file_tf.loc[len(self.file_tf)] = res

            return self.file_tf
        else:
            return self.file

    def get_quotes(self, ticker, start_date: datetime, end_date: datetime, tf: str):
        # если все параметры остались те же самые (сменилась тема (trigger для update_graph))
        if all([self.ticker == ticker, self.start_date == start_date, self.end_date == end_date, self.tf == tf]):
            return self.file_tf
        else:
            self._download(ticker, start_date, end_date)
            return self._change_tf(tf)

    def get_price(self, dt, ptype: str = 'OPEN'):
        return self.file.loc[self.file['DATE'] == dt][ptype].values[0]


if __name__ == '__main__':
    quotes = Quotes()
    print(quotes.get_quotes('SBER - Сбербанк', datetime(2020, 5, 14, 10, 0),
                            datetime(2020, 5, 14, 18, 0), '1 мин.').head(5))
