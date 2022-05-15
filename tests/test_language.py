import datetime

from iso639 import Language
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
    assert Language.match("invalid input") is None
    assert Language.from_part3("Fra") is None  # case-sensitive!
    assert Language.from_part3("unknown code") is None
