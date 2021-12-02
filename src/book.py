from datetime import datetime
import requests
from bs4 import BeautifulSoup


def decorator_attr_err(func):
    def wrapper(*args):
        try:
            func(*args)
        except AttributeError:
            return None

    return wrapper


class Book:

    def __init__(self, url):
        self.url = url
        self.page = requests.get(url).content
        self.soup = BeautifulSoup(self.page, 'html.parser')

    @property
    def book_id(self):
        return self.url.split('/')[-2]

    @property
    def title(self):
        return (
            self.soup
                .find('div', {'id': 'book-info'})
                .find('h1')
                .get_text()
                .strip()
        )

    @property
    @decorator_attr_err
    def author(self):
        return (
            self.soup
                .find('span', {'class': 'author pb-2'})
                .find('a')
                .get_text()
        )

    @property
    @decorator_attr_err
    def author_url(self):
        if self.author:
            return (
                self.soup
                    .find('span', {'class': 'author pb-2'})
                    .find('a')['href']
            )
        else:
            return None

    @property
    @decorator_attr_err
    def series(self):
        return (
            self.soup
                .find('span', {'class': 'd-none d-sm-block mt-1'})
                .find('a')
                .get_text()
                .strip()
        )

    @property
    @decorator_attr_err
    def series_url(self):
        if self.series:
            return 'https://lubimyczytac.pl' + (
                self.soup
                    .find('span', {'class': 'd-none d-sm-block mt-1'})
                    .find('a')['href']
            )
        else:
            return None

    @property
    def book_details(self):
        dl = (
            self.soup
                .find('div', {'id': 'book-details'})
                .find('dl')
        )

        dt = dl.find_all('dt')
        dd = dl.find_all('dd')
        result = dict()
        for col in [
            'Kategoria', 'Tytuł oryginału', 'Wydawnictwo',
            'Data Wydania', 'Data 1. wyd. pol.', 'Data 1. wydania',
            'Czas czytania', 'Liczba stron', 'Język', 'ISBN', 'Tłumacz'
        ]:
            result[col] = None

        for k, v in zip(dt, dd):
            try:
                key = k.get_text().strip()
                if key[-1] == ':':
                    key = key[:-1]
                value = v.get_text().strip()
                result[key] = value
            except AttributeError:
                continue

        return result

    @property
    def rates(self):
        value = (
            self.soup
            .find('div', {'class': 'col-lg-8 col-xl-9 chartBarsRate-hld'})
            .find_all('div', {'class': 'col-9 col-xl-2 order-2 order-xl-3 d-flex align-items-center'})
        )
        result = dict()
        rate = 10
        for i in value:
            rate_count = i.find('a')['data-count']
            if rate_count == '':
                rate_count = '0'
            result[rate] = rate_count
            rate -= 1

        return result

    @property
    def main_qties(self):
        data = (
            self.soup
                .find('div', {'class': 'd-flex flex-wrap justify-content-around px-3'})
        )
        result = dict()
        if data:
            for k, v in zip(['opinie', 'oceny', 'dyskusje'], data.find_all('a')):
                result[k] = ''.join(d for d in v.get_text().strip() if d.isdigit())
        else:
            for i in ['opinie', 'oceny', 'dyskusje']:
                result[i] = '0'

        return result

    @property
    def rating(self):
        return (
            self.soup
                .find('span', {'class': 'big-number'})
                .get_text()
                .strip()
                .replace(',', '.')
        )

    @property
    def insert_query(self):

        columns = [
            'book_id', 'book_url', 'title', 'author', 'author_url', 'category',
            'series', 'series_url', 'title_org', 'publisher', 'publication_date',
            'first_publication_date_poland', 'first_publication_date', 'reading_time',
            'pages', 'language', 'ISBN', 'translator', 'rates_count', 'opinions_count',
            'discussions_count', 'rating', 'rate_10', 'rate_9', 'rate_8', 'rate_7', 'rate_6',
            'rate_5', 'rate_4', 'rate_3', 'rate_2', 'rate_1', 'status_datetime'
        ]

        insert_dict = dict()
        for col in columns:
            insert_dict[col] = None

        insert_dict = {
            'book_id': self.book_id,
            'book_url': self.url,
            'title': self.title,
            'author': self.author,
            'author_url': self.author_url,
            'category': self.book_details['Kategoria'],
            'series': self.series,
            'series_url': self.series_url,
            'title_org': self.book_details['Tytuł oryginału'],
            'publisher': self.book_details['Wydawnictwo'],
            'publication_date': self.book_details['Data wydania'],
            'first_publication_date_poland': self.book_details['Data 1. wyd. pol.'],
            'first_publication_date': self.book_details['Data 1. wydania'],
            'reading_time': self.book_details['Czas czytania'],
            'pages': self.book_details['Liczba stron'],
            'language': self.book_details['Język'],
            'ISBN': self.book_details['ISBN'],
            'translator': self.book_details['Tłumacz'],
            'rates_count': self.main_qties['oceny'],
            'opinions_count': self.main_qties['opinie'],
            'discussions_count': self.main_qties['dyskusje'],
            'rating': self.rating,
            'status_datetime': datetime.today()
        }

        for k, v in self.rates.items():
            insert_dict['rate_%d' % k] = v

        keys, values = zip(*insert_dict.items())
        columns_str = ', '.join(k for k in keys)
        values_str = ', '.join("'" + str(v).replace("'", "''") + "'" for v in values)

        query = f"""
            INSERT INTO lubimyczytac.books ({columns_str})
            VALUES ({values_str})
        """.replace(" 'None',", ' NULL,').replace(" '',", ' NULL,')

        return query
