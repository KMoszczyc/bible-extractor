import pytest

from extract import is_book_start, is_verse_start


@pytest.mark.parametrize(
    "line_before, line, books, expected",
    [
        # Happy path tests
        ("*T-1m*", "Księga Rodzaju", ["Księga Rodzaju", "Księga Wyjścia"], True),  # ID: happy_path_1
        ("*T-2m*", "Księga Wyjścia", ["Księga Rodzaju", "Księga Wyjścia"], True),  # ID: happy_path_2

        # Edge cases
        ("*T-1m*", "Księga Kapłańska", ["Księga Rodzaju", "Księga Wyjścia"], False),  # ID: edge_case_1
        ("*T-1m*", "", ["Księga Rodzaju", "Księga Wyjścia"], False),  # ID: edge_case_2
        ("*T-1m*", "Księga Rodzaju", [], False),  # ID: edge_case_4
        ("*T-1m*", "Księga Rodzaju", ["Księga Kapłańska"], False),  # ID: edge_case_5
        ("blablabla", "Księga Rodzaju", ["Księga Rodzaju"], False),  # ID: edge_case_5
        ("", "Księga Rodzaju", ["Księga Rodzaju"], False),  # ID: edge_case_5

        # Error cases
        ("*T-1m3*", "Warszawska Gdańska Warszawsko-Praska", ["Księga Rodzaju", "Księga Wyjścia"], False),  # ID: error_case_1
        ("*T-1m*", "", ["Księga Rodzaju", "Księga Wyjścia"], False),  # ID: error_case_2
        ("*T-1m3*", "", ["Księga Rodzaju", "Księga Wyjścia"], False),  # ID: error_case_3
    ]
)
def test_detect_book_start(line_before, line, books, expected):
    result = is_book_start(line_before, line, books)
    assert result == expected


@pytest.mark.parametrize("line, expected", [
    # Happy path tests
    ("1. In the beginning God created the heaven and the earth.", True),  # ID: verse_start_with_single_digit
    ("12. And God said, Let there be light: and there was light.", True),  # ID: verse_start_with_double_digits
    ("123. And God saw the light, that it was good: and God divided the light from the darkness.", True),  # ID: verse_start_with_triple_digits

    # Edge cases
    ("1. ", True),  # ID: verse_start_with_single_digit_and_space
    ("12. ", True),  # ID: verse_start_with_double_digits_and_space
    ("123. ", True),  # ID: verse_start_with_triple_digits_and_space
    ("In the beginning God created the heaven and the earth.", False),  # ID: no_verse_start
    ("", False),  # ID: empty_string

    # Error cases
    ("1 In the beginning God created the heaven and the earth.", False),  # ID: missing_period_after_digit
    ("1In the beginning God created the heaven and the earth.", False),  # ID: multiple_periods
    ("Verse 1. In the beginning God created the heaven and the earth.", False),  # ID: text_before_verse_start
])
def test_is_verse_start(line, expected):
    result = is_verse_start(line)
    assert bool(result) == expected
