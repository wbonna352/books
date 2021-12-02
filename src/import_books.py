import requests
from bs4 import BeautifulSoup
import psycopg2

from book import Book


def get_books_url_from_one_page(url):
    page = requests.get(url).content
    soup = BeautifulSoup(page, 'html.parser')

    books_divs = soup.find_all('div', {'class': 'authorAllBooks__single'})
    urls = []
    for book in books_divs:
        urls.append('https://lubimyczytac.pl' + book.find('a')['href'])

    return urls


URL = 'https://lubimyczytac.pl/katalog?page=%d&catalogSortBy=ratings-desc'

host = 'localhost'
username = 'postgres'
password = 'postgres'
database = 'books'

conn = psycopg2.connect(
    host=host,
    database=database,
    user=username,
    password=password
)

cursor = conn.cursor()

books_in_page = 1
i = 3289
while i < 20_000:
    i += 1
    print(i)
    books = get_books_url_from_one_page(URL % i)
    books_in_page = len(books)
    for b in books:

        print(b)
        book = Book(b)
        cursor.execute(f"SELECT book_id FROM lubimyczytac.books WHERE book_url = '{b}'")
        if cursor.fetchone():
            cursor.execute(f"DELETE FROM lubimyczytac.books WHERE book_url = '{b}'")
            conn.commit()
        cursor.execute(book.insert_query)
        conn.commit()

conn.close()
