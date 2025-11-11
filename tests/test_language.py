import datetime

from iso639 import Language, ALL_LANGUAGES, DATA_LAST_UPDATED, LanguageNotFoundError
from iso639.language import Name

import pytest


@pytest.mark.parametrize(
    "user_input, strict_case, expected_part3",
    [
        ("fra", True, "fra"),
        (" fra  ", True, "fra"),
        ("fra", False, "fra"),
        ("FRA", True, None),
        ("FRA", False, "fra"),
        (" FRA  ", False, "fra"),
        ("Fra", True, None),
        ("Fra", False, "fra"),
        (" Fra  ", False, "fra"),
        ("French", True, "fra"),
        ("French", False, "fra"),
        ("FRENCH", True, None),
        ("FRENCH", False, "fra"),
        (" FRENCH  ", False, "fra"),
        ("french", True, None),
        ("french", False, "fra"),
        (" french  ", False, "fra"),
        ("Castilian", True, "spa"),
    ],
)
def test_match(user_input, strict_case, expected_part3):
    if expected_part3 is None:
        with pytest.raises(LanguageNotFoundError):
            Language.match(user_input, strict_case=strict_case)
    else:
        actual_part3 = Language.match(user_input, strict_case=strict_case).part3
        assert actual_part3 == expected_part3


@pytest.mark.parametrize(
    "user_input, expected_part3",
    [
        ("fra", "fra"),
        (" fra  ", "fra"),
        ("FRA", None),
        (" FRA  ", None),
        ("Fra", None),
        (" Fra  ", None),
        ("French", "fra"),
        ("FRENCH", None),
        (" FRENCH  ", None),
        ("french", None),
        (" french  ", None),
        ("Castilian", "spa"),
    ],
)
def test_match_no_strict_case_kwarg(user_input, expected_part3):
    if expected_part3 is None:
        with pytest.raises(LanguageNotFoundError):
            Language.match(user_input)
    else:
        actual_part3 = Language.match(user_input).part3
        assert actual_part3 == expected_part3


def test_name():
    name = Name("foo", "bar")
    assert name.print == "foo"
    assert name.inverted == "bar"


def test_attributes_cantonese():
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


def test_attributes_french():
    language = Language.match("fra")
    assert language.part3 == "fra"
    assert language.part2b == "fre"
    assert language.part2t == "fra"
    assert language.part1 == "fr"
    assert language.scope == "I"
    assert language.type == "L"
    assert language.status == "A"
    assert language.name == "French"
    assert language.comment is None
    assert language.other_names is None
    assert language.macrolanguage is None
    assert language.retire_reason is None
    assert language.retire_change_to is None
    assert language.retire_remedy is None
    assert language.retire_date is None


def test_retired_codes():
    lang1 = Language.match("bvs")
    lang2 = Language.from_part3("bvs")
    assert lang1 == lang2
    assert lang1.name == "Belgian Sign Language"
    assert lang1.status == "R"
    assert lang1.retire_reason == "S"
    assert lang1.retire_date == datetime.date(2007, 7, 18)
    assert lang1.retire_remedy == (
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
    assert DATA_LAST_UPDATED == datetime.date(2025, 10, 15), "Need to update README.md"


def test_all_languages():
    assert type(ALL_LANGUAGES) is set
    # Defining `len_all_languages` so that when the assertion fails,
    # the error message is more informative.
    len_all_languages = len(ALL_LANGUAGES)
    assert len_all_languages == 8311, "Need to update README.md"
    lang = list(ALL_LANGUAGES)[0]
    assert type(lang) is Language


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
