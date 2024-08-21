import json
import pandas as pd
from enum import Enum

BIBLE_RAW_PATH = 'data/raw/raw_bible.txt'
BOOK_MAP_PATH = 'data/raw/book_map.json'


def read_str_file(path):
    with open(path, 'r') as f:
        return f.read().splitlines()


def read_json(path):
    with open(path) as f:
        return json.load(f)


def extract(book_map, raw_bible):
    df = pd.DataFrame(columns=['book', 'chapter', 'verse', 'text'])


def detect_book_start(line_before, line, books):
    return line_before.count('*') >= 2 and line in books


def detect_chapter_start(line_before, line):
    return line_before.count('*') >= 2 and line.count('*' >= 2)


def detect_trash_headers(line, line_after, books):
    return line.count('*') >= 2 and line not in books


def has_numbers(text):
    return any(char.isdigit() for char in text)


class SeachMode(Enum):
    GO_TO_NEXT_BOOK = 1
    GO_TO_CHAPTER_START = 2
    READING_VERSES = 3


def etl():
    raw_bible = read_str_file(BIBLE_RAW_PATH)
    book_map = read_json(BOOK_MAP_PATH)
    book_rev_map = dict((v, k) for k, v in book_map.items())
    books = list(book_map.values())

    print(books)
    print(book_map)
    print(book_rev_map)

    print(raw_bible[:100])


if __name__ == '__main__':
    etl()
