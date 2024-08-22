import csv
import json
import re

import pandas as pd
from enum import Enum

BIBLE_RAW_PATH = 'data/raw/raw_bible.txt'
BOOK_MAP_PATH = 'data/raw/book_map.json'

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 2000)
pd.set_option('display.float_format', '{:20,.2f}'.format)
pd.set_option('display.max_colwidth', None)


# Parse cycle: Start book -> start chapter -> read verses -> end_chapter -> end book
#                                  ^------<------<---------<-----|

def read_str_file(path):
    with open(path, 'r') as f:
        return f.read().splitlines()


def read_json(path):
    with open(path) as f:
        return json.load(f)


def extract(book_map, raw_bible):
    df = pd.DataFrame(columns=['book', 'chapter', 'verse', 'text'])


def is_book_start(line_before, line, books):
    return line_before.count('*') >= 2 and line in books


def detect_chapter_start(line_before, line, books):
    return ''


def detect_chapter_end(line):
    return 'Dostępne przekłady' in line


def skip_trash_headers(line, line_after):
    skip = 'Biblia Tysiąclecia' in line
    # skip = 'Biblia Tysiąclecia' in line and line_after.count('*') >= 2
    return (True, 2) if skip else (False, 0)


def is_chapter_start(line):
    pattern = r'^\d+\s[A-Za-z]+'
    return re.search(pattern, line)


def is_verse_start(line):
    pattern = r'^\d+\..*'
    return re.search(pattern, line)


def has_numbers(text):
    return any(char.isdigit() for char in text)


def parse_number(text):
    return int(text)


def is_int(text):
    try:
        int(text)
        return True
    except ValueError:
        return False


class State(Enum):
    BOOK_STARTING = 1
    CHAPTER_STARTING = 2
    READING_VERSES = 3
    CHAPTER_ENDING = 4
    BOOK_ENDING = 5
    NO_STATE = 6


def etl():
    raw_bible = read_str_file(BIBLE_RAW_PATH)
    book_map = read_json(BOOK_MAP_PATH)

    rows = []
    book_rev_map = dict((v, k) for k, v in book_map.items())
    books = list(book_map.values())

    current_book = None
    current_chapter = None
    current_verse = None
    current_verse_text = None
    current_mode = State.BOOK_ENDING
    i = 1

    while i < len(raw_bible) - 1:
        line = raw_bible[i]
        line_before = raw_bible[i - 1]
        line_after = raw_bible[i + 1]
        line_split = line.split()

        if current_mode == State.CHAPTER_STARTING and is_chapter_start(line):
            current_mode = State.READING_VERSES
            current_verse = 1
            current_chapter = int(line_split[0])
            current_verse_text = ' '.join(line_split[1:])
        elif current_mode == State.READING_VERSES:
            skip, skip_count = skip_trash_headers(line, line_after)
            if skip:
                i += skip_count
                continue

            if detect_chapter_end(line):  # chapter is ending
                current_mode = State.CHAPTER_STARTING
                rows.append(create_row(current_book, current_chapter, current_verse, current_verse_text))

            if is_verse_start(line):  # new verse
                rows.append(create_row(current_book, current_chapter, current_verse, current_verse_text))
                num_s = line_split[0].split('.')[0]
                current_verse = parse_number(num_s)
                current_verse_text = ' '.join(line_split[1:])
            else:  # old verse
                current_verse_text += f" {line}"
        if is_book_start(line_before, line, books):
            current_book = line
            current_mode = State.CHAPTER_STARTING

        i += 1

        if i % 1000 == 0:
            print(i, current_mode, current_book, current_chapter, current_verse)

    df = pd.DataFrame(rows)
    df['abbreviation'] = df['book'].map(book_rev_map)
    df = df[['abbreviation', 'book', 'chapter', 'verse', 'text']]
    merged_df = merge_related_verses(df)

    print(merged_df.head(100))
    df.to_parquet('data/processed/bible.parquet', index=False)
    df.to_csv('data/processed/bible.csv', index=False, quoting=csv.QUOTE_ALL)

    merged_df.to_parquet('data/processed/merged_bible.parquet', index=False)
    merged_df.to_csv('data/processed/merged_bible.csv', index=False, quoting=csv.QUOTE_ALL)

    print(books)
    print(book_map)
    print(book_rev_map)

    print(df.head(1000))


def merge_related_verses(df):
    merged_rows = []
    current_row = None
    merge_count = 0
    max_verse = None
    for row in df.to_dict(orient="records"):
        if row['text'][0].islower():
            current_row['text'] += ' ' + row['text']
            max_verse = str(row['verse'])
            merge_count += 1
        else:
            if max_verse is not None:
                current_row['verse'] = str(current_row['verse']) + '-' + max_verse
            if current_row is None:
                current_row = row
            merged_rows.append(current_row)
            current_row = row
            max_verse = None

    print(f"Merged {merge_count} verses, {len(df)} -> {len(merged_rows)}")

    merged_df = pd.DataFrame(merged_rows)
    merged_df['verse'] = merged_df['verse'].astype(str)

    return merged_df


def create_row(book, chapter, verse, text):
    return {"book": book, "chapter": chapter, "verse": verse, "text": text}


def print_full():
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 2000)
    pd.set_option('display.float_format', '{:20,.2f}'.format)
    pd.set_option('display.max_colwidth', None)


# def starting_book():


if __name__ == '__main__':
    etl()
