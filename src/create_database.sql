--CREATE DATABASE books;

CREATE SCHEMA lubimyczytac;

CREATE TABLE lubimyczytac.Books
(
    book_id INT PRIMARY KEY,
    book_url TEXT,
    title TEXT NOT NULL,
    author TEXT,
    author_url TEXT,
    category TEXT,
    series TEXT,
    series_url TEXT,
    title_org TEXT,
    publisher TEXT,
    publication_date DATE,
    first_publication_date_poland DATE,
    first_publication_date DATE,
    reading_time TEXT,
    pages INT,
    language TEXT,
    ISBN TEXT,
    translator TEXT,
    rates_count INT,
    opinions_count INT,
    discussions_count INT,
    rating NUMERIC(3,1),
    rate_10 INT,
    rate_9 INT,
    rate_8 INT,
    rate_7 INT,
    rate_6 INT,
    rate_5 INT,
    rate_4 INT,
    rate_3 INT,
    rate_2 INT,
    rate_1 INT,
    status_datetime TIMESTAMP
);