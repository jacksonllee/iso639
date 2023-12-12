import datetime

from iso639 import Language, ALL_LANGUAGES, DATA_LAST_UPDATED, LanguageNotFoundError
from iso639.language import Name

import pytest


@pytest.mark.parametrize(
    "user_input, expected_part3",
    [
        ("fra", "fra"),
        ("fre", "fra"),
        ("fr", "fra"),
        ("French", "fra"),
        ("Castilian", "spa"),
    ],
)
def test_match(user_input, expected_part3):
    actual_part3 = Language.match(user_input).part3
    assert actual_part3 == expected_part3


def test_name():
    name = Name("foo", "bar")
    assert name.print == "foo"
    assert name.inverted == "bar"


def test_attributes():
    language = Language.match("yue")
    assert language.part3 == "yue"
    assert language.part2b is None
    assert language.part2t is None
    assert language.part1 is None
    assert language.scope == "I"
    assert language.type == "L"
    assert language.status == "A"
    assert language.name == "Yue Chinese"
    assert language.comment is None
    assert language.other_names == [Name("Yue Chinese", "Chinese, Yue")]
    assert language.macrolanguage == "zho"
    assert language.retire_reason is None
    assert language.retire_change_to is None
    assert language.retire_remedy is None
    assert language.retire_date is None


def test_retired_codes():
    language = Language.match("bvs")
    assert language.name == "Belgian Sign Language"
    assert language.status == "R"
    assert language.retire_reason == "S"
    assert language.retire_date == datetime.date(2007, 7, 18)
    assert language.retire_remedy == (
        "Split into Langue des signes de Belgique Francophone [sfb], "
        "and Vlaamse Gebarentaal [vgt]"
    )


def test_invalid_inputs():
    with pytest.raises(LanguageNotFoundError):
        Language.match("invalid input")
    with pytest.raises(LanguageNotFoundError):
        Language.from_part3("Fra")  # case-sensitive!
    with pytest.raises(LanguageNotFoundError):
        Language.from_part3("unknown code")


def test_data_last_updated():
    assert DATA_LAST_UPDATED == datetime.date(2023, 1, 23), "Need to update README.md"


def test_all_languages():
    assert type(ALL_LANGUAGES) is list
    assert type(ALL_LANGUAGES[0]) is Language
    assert len(ALL_LANGUAGES) == 7916, "Need to update README.md"

    lang = ALL_LANGUAGES[0]
    assert lang.part3 == "aaa", "Need to update README.md"
    assert lang.name == "Ghotuo", "Need to update README.md"


def test_eq():
    yue1 = Language.match("yue")
    yue2 = Language.match("yue")
    fra = Language.match("fra")

    assert yue1.part3 == yue2.part3 == "yue"
    assert fra.part3 == "fra"
    assert yue1 == yue2
    assert yue1 != fra


def test_hashable():
    """Language class instances are hashable, e.g., can be in a set.
    See https://github.com/jacksonllee/iso639/issues/3
    """
    cat = Language.match("cat")
    assert cat.part3 == "cat"
    assert type(cat.other_names) is list  # Need a list attr for the hashing test...
    hash(cat)  # Shouldn't error!
    assert len({cat, cat, cat}) == 1
