"""The Language class."""

import datetime
import functools
import os
import sqlite3
from dataclasses import dataclass

from typing import Iterable, List, Optional, Tuple


_DB = sqlite3.connect(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "languages.db"),
    check_same_thread=False,
)


class LanguageNotFoundError(Exception):
    pass


@dataclass(frozen=True)
class Name:
    """Represents an alternative name of a language."""

    __slots__ = ("print", "inverted")
    print: str
    inverted: str


@dataclass(frozen=True)
class Language:
    """Represents a language in the ISO 639-3 charts."""

    __slots__ = (
        # From the "codes" table
        "part3",
        "part2b",
        "part2t",
        "part1",
        "scope",
        "type",
        "status",
        "name",
        "comment",
        # From the "name_index" table
        "other_names",
        # From the "macrolanguages" table
        "macrolanguage",
        # From the "retirements" table
        "retire_reason",
        "retire_change_to",
        "retire_remedy",
        "retire_date",
    )

    # From the "codes" table
    part3: str
    part2b: str
    part2t: str
    part1: str
    scope: str
    type: str
    status: str
    name: str
    comment: str

    # From the "name_index" table
    other_names: List[Name]

    # From the "macrolanguages" table
    macrolanguage: str

    # From the "retirements" table
    retire_reason: str
    retire_change_to: str
    retire_remedy: str
    retire_date: datetime.date

    def __hash__(self) -> int:
        return hash(self.part3)

    def __eq__(self, other) -> bool:
        return isinstance(other, Language) and self.part3 == other.part3

    @classmethod
    def match(cls, user_input) -> "Language":
        """Return a ``Language`` instance by matching on the user input.

        Parameters
        ----------
        user_input : str
            A language code or name.

        Returns
        -------
        Language

        Notes
        -----
        At a high level, `Language.match` assumes the input is more likely to be
        a language code rather than a language name.
        Beyond that, the precise order in matching is as follows:

        * ISO 639-3 codes (among the active codes)
        * ISO 639-2 (bibliographic) codes
        * ISO 639-2 (terminological) codes
        * ISO 639-1 codes
        * ISO 639-3 codes (among the retired codes)
        * ISO 639-3 reference language names
        * ISO 639-3 alternative language names (the "print" ones)
        * ISO 639-3 alternative language names (the "inverted" ones)
        """
        # Order of (table, field) pairs to query `languages.db`.
        # Bias towards (and therefore prioritize) the user input being
        # a language code rather than a language name.
        query_order = (
            ("codes", "Id"),
            ("codes", "Part2B"),
            ("codes", "Part2T"),
            ("codes", "Part1"),
            ("retirements", "Id"),
            ("codes", "Ref_Name"),
            ("name_index", "Print_Name"),
            ("name_index", "Inverted_Name"),
        )
        return _get_language(user_input, query_order)

    @classmethod
    def from_part3(cls, user_input) -> "Language":
        """Return a ``Language`` instance from an ISO 639-3 code."""
        return _get_language(user_input, (("codes", "Id"),))

    @classmethod
    def from_part2b(cls, user_input) -> "Language":
        """Return a ``Language`` instance from an ISO 639-2 (bibliographic) code."""
        return _get_language(user_input, (("codes", "Part2B"),))

    @classmethod
    def from_part2t(cls, user_input) -> "Language":
        """Return a ``Language`` instance from an ISO 639-2 (terminological) code."""
        return _get_language(user_input, (("codes", "Part2T"),))

    @classmethod
    def from_part1(cls, user_input) -> "Language":
        """Return a ``Language`` instance from an ISO 639-1 code."""
        return _get_language(user_input, (("codes", "Part1"),))

    @classmethod
    def from_name(cls, user_input) -> "Language":
        """Return a ``Language`` instance from an ISO 639-3 reference language name."""
        query_order = (
            ("codes", "Ref_Name"),
            ("name_index", "Print_Name"),
            ("name_index", "Inverted_Name"),
        )
        return _get_language(user_input, query_order)


def _query_db(table: str, field: str, x: str) -> sqlite3.Cursor:
    return _DB.execute(f"SELECT * FROM {table} where {field} = ?", (x,))  # nosec


@functools.lru_cache()
def _get_language(
    user_input: str, query_order: Optional[Iterable[Tuple[str, str]]] = None
) -> Language:
    """Create a ``Language`` instance.

    Parameters
    ----------
    user_input : str
        The user-provided language code or name.
    query_order : Iterable[Tuple[str, str], optional
        An iterable of (table, field) pairs to specify query order.
        If not provided, no queries are made and `part3` is assumed to be
        an actual ISO 639-3 code.

    Returns
    -------
    Language

    Raises
    ------
    LanguageNotFoundError
        If `part3` isn't a language name or code
    """

    if query_order is not None:
        for table, field in query_order:
            result = _query_db(table, field, user_input).fetchone()
            if result:
                part3 = result[0]
                break
        else:
            raise LanguageNotFoundError(
                f"{user_input!r} isn't an ISO language code or name"
            )
    else:
        part3 = user_input

    def query_for_id(table: str) -> sqlite3.Cursor:
        id_field = "I_Id" if table == "macrolanguages" else "Id"
        return _query_db(table, id_field, part3)

    from_codes = query_for_id("codes").fetchone()
    from_name_index = query_for_id("name_index").fetchall()
    from_macrolanguages = query_for_id("macrolanguages").fetchone()
    from_retirements = query_for_id("retirements").fetchone()

    macrolanguage = from_macrolanguages[0] if from_macrolanguages else None
    retire_reason = from_retirements[2] if from_retirements else None
    retire_change_to = from_retirements[3] if from_retirements else None
    retire_remedy = from_retirements[4] if from_retirements else None
    retire_date = (
        datetime.datetime.strptime(from_retirements[5], "%Y-%m-%d").date()
        if from_retirements
        else None
    )

    if from_codes:
        # The ISO 639-3 code is active.
        part2b = from_codes[1]
        part2t = from_codes[2]
        part1 = from_codes[3]
        scope = from_codes[4]
        type = from_codes[5]
        status = "A"
        ref_name = from_codes[6]
        comment = from_codes[7]
        other_names = [
            Name(print_name, inverted_name)
            for _, print_name, inverted_name in from_name_index
            if not (ref_name == print_name == inverted_name)
        ] or None

    else:
        # The ISO 639-3 code is retired.
        part2b = None
        part2t = None
        part1 = None
        scope = "I"
        type = None
        status = "R"
        ref_name = from_retirements[1]
        comment = None
        other_names = None

    language = Language(
        part3=part3,
        part2b=part2b,
        part2t=part2t,
        part1=part1,
        scope=scope,
        type=type,
        status=status,
        name=ref_name,
        comment=comment,
        other_names=other_names,
        macrolanguage=macrolanguage,
        retire_reason=retire_reason,
        retire_change_to=retire_change_to,
        retire_remedy=retire_remedy,
        retire_date=retire_date,
    )

    return language


@functools.lru_cache()
def _get_all_languages() -> List[Language]:
    return [
        _get_language(part3)
        for part3 in [row[0] for row in _DB.execute("SELECT Id FROM codes").fetchall()]
    ]
