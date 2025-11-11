"""The Language class."""

from __future__ import annotations

import datetime
from dataclasses import dataclass

from typing import NoReturn

from ._data import (
    _PART3_TO_CODES,
    _PART3_TO_NAME_INDEX,
    _PART3_TO_MACROLANGUAGES,
    _PART3_TO_RETIREMENTS,
    _PART2B_TO_PART3,
    _PART2T_TO_PART3,
    _PART1_TO_PART3,
    _REF_NAME_TO_PART3,
    _PRINT_NAME_TO_PART3,
    _INVERTED_NAME_TO_PART3,
    _CodesColumn,
    _NameIndexColumn,
    _RetirementsColumn,
    _MacrolanguagesColumn,
    _COLUMN_TYPE,
)


_STRING_CLEANING_FUNCS = [lambda x: x.lower(), lambda x: x.title()]


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
    part2b: str | None
    part2t: str | None
    part1: str | None
    scope: str
    type: str | None
    status: str
    name: str
    comment: str | None

    # From the "name_index" table
    other_names: list[Name] | None

    # From the "macrolanguages" table
    macrolanguage: str | None

    # From the "retirements" table
    retire_reason: str | None
    retire_change_to: str | None
    retire_remedy: str | None
    retire_date: datetime.date | None

    def __hash__(self) -> int:
        return hash(self.part3)

    def __eq__(self, other) -> bool:
        return isinstance(other, Language) and self.part3 == other.part3

    @classmethod
    def match(cls, user_input: str, /, *, strict_case: bool = True) -> Language:
        """Return a ``Language`` instance by matching on the user input.

        Parameters
        ----------
        user_input : str
            A language code or name.
        strict_case : bool, optional
            Defaults to ``True``, for enforcing strict case sensitivity.
            If ``False`` and if ``user_input`` doesn't find a match,
            further match attempts will be made with the all-lowercase version of
            ``user_input`` (``"foobar"``) and the title-case version of ``user_input``
            (``"Foobar"``).

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
        # Order of columns to query the data tables.
        # Bias towards (and therefore prioritize) the user input being
        # a language code rather than a language name.
        query_order: list[_COLUMN_TYPE] = [
            _CodesColumn.ID,
            _CodesColumn.PART2B,
            _CodesColumn.PART2T,
            _CodesColumn.PART1,
            _RetirementsColumn.ID,
            _CodesColumn.REF_NAME,
            _NameIndexColumn.PRINT_NAME,
            _NameIndexColumn.INVERTED_NAME,
        ]
        return _PART3_TO_LANGUAGES[_get_part3(user_input, query_order, strict_case)]

    @classmethod
    def from_part3(cls, user_input: str, /) -> Language:
        """Return a ``Language`` instance from an ISO 639-3 code."""
        return _PART3_TO_LANGUAGES[
            _get_part3_exact(user_input, [_CodesColumn.ID, _RetirementsColumn.ID])
        ]

    @classmethod
    def from_part2b(cls, user_input: str, /) -> Language:
        """Return a ``Language`` instance from an ISO 639-2 (bibliographic) code."""
        return _PART3_TO_LANGUAGES[_get_part3_exact(user_input, [_CodesColumn.PART2B])]

    @classmethod
    def from_part2t(cls, user_input: str, /) -> Language:
        """Return a ``Language`` instance from an ISO 639-2 (terminological) code."""
        return _PART3_TO_LANGUAGES[_get_part3_exact(user_input, [_CodesColumn.PART2T])]

    @classmethod
    def from_part1(cls, user_input: str, /) -> Language:
        """Return a ``Language`` instance from an ISO 639-1 code."""
        return _PART3_TO_LANGUAGES[_get_part3_exact(user_input, [_CodesColumn.PART1])]

    @classmethod
    def from_name(cls, user_input: str, /) -> Language:
        """Return a ``Language`` instance from an ISO 639-3 reference language name."""
        query_order: list[_COLUMN_TYPE] = [
            _CodesColumn.REF_NAME,
            _NameIndexColumn.PRINT_NAME,
            _NameIndexColumn.INVERTED_NAME,
        ]
        return _PART3_TO_LANGUAGES[_get_part3_exact(user_input, query_order)]


def _raise_language_not_found_error(user_input: str) -> NoReturn:
    raise LanguageNotFoundError(f"{user_input!r} isn't an ISO language code or name")


def _get_part3(
    user_input: str, query_order: list[_COLUMN_TYPE], strict_case: bool = True
) -> str:
    """Get the part 3 code of a language.

    Parameters
    ----------
    user_input : str
        The user-provided language code or name.
    query_order : List[_COLUMN_TYPE]
        A list of columns to specify query order.
    strict_case : bool, optional
        Defaults to ``True``, for enforcing strict case sensitivity.
        If ``False`` and if ``user_input`` doesn't find a match,
        further match attempts will be made with the all-lowercase version of
        ``user_input`` (``"foobar"``) and the title-case version of ``user_input``
        (``"Foobar"``).

    Returns
    -------
    str

    Raises
    ------
    LanguageNotFoundError
        If `part3` isn't a language name or code
    """
    try:
        return _get_part3_exact(user_input, query_order)
    except LanguageNotFoundError as e:
        if strict_case:
            raise e
        else:
            for func in _STRING_CLEANING_FUNCS:
                try:
                    return _get_part3_exact(func(user_input), query_order, user_input)
                except LanguageNotFoundError:
                    continue
            else:
                _raise_language_not_found_error(user_input)


def _get_part3_exact(
    user_input: str,
    query_order: list[_COLUMN_TYPE],
    original_user_input: str | None = None,
) -> str:
    """Get the part 3 code of a language.

    Parameters
    ----------
    user_input : str
        The user-provided language code or name.
    query_order : list[_COLUMN_TYPE]
        A list of columns to specify query order.
    original_user_input : str, optional
        The original user input. Default is `None`.
        This argument is used when the user input has been cleaned.

    Returns
    -------
    str

    Raises
    ------
    LanguageNotFoundError
        If `part3` isn't a language name or code
    """
    user_input = user_input.strip()
    part3: str | None = None
    for column in query_order:
        if column == _CodesColumn.ID:
            if user_input in _PART3_TO_CODES:
                return user_input
        elif column == _CodesColumn.PART2B:
            part3 = _PART2B_TO_PART3.get(user_input)
        elif column == _CodesColumn.PART2T:
            part3 = _PART2T_TO_PART3.get(user_input)
        elif column == _CodesColumn.PART1:
            part3 = _PART1_TO_PART3.get(user_input)
        elif column == _RetirementsColumn.ID:
            if user_input in _PART3_TO_RETIREMENTS:
                return user_input
        elif column == _CodesColumn.REF_NAME:
            part3 = _REF_NAME_TO_PART3.get(user_input)
        elif column == _NameIndexColumn.PRINT_NAME:
            part3 = _PRINT_NAME_TO_PART3.get(user_input)
        elif column == _NameIndexColumn.INVERTED_NAME:
            part3 = _INVERTED_NAME_TO_PART3.get(user_input)
        else:
            raise ValueError(f"Invalid column: {column}")
        if part3 is not None:
            break

    if part3 is None:
        _raise_language_not_found_error(original_user_input or user_input)

    return part3


def _get_language(part3: str) -> Language:
    """Create a ``Language`` instance.

    Parameters
    ----------
    part3 : str
        Part 3 code of the language.

    Returns
    -------
    Language
    """
    from_codes = _PART3_TO_CODES.get(part3)
    from_macrolanguages = _PART3_TO_MACROLANGUAGES.get(part3)
    from_retirements = _PART3_TO_RETIREMENTS.get(part3)

    ref_name = (
        from_codes[_CodesColumn.REF_NAME]
        if from_codes
        else from_retirements[_RetirementsColumn.REF_NAME]  # type: ignore
    )

    other_names: list[Name] | None = []
    for row in _PART3_TO_NAME_INDEX.get(part3, []):
        p, i = row[_NameIndexColumn.PRINT_NAME], row[_NameIndexColumn.INVERTED_NAME]
        if not ref_name == p == i:
            other_names.append(Name(p, i))  # type: ignore
    other_names = other_names or None

    macrolanguage = (from_macrolanguages or {}).get(_MacrolanguagesColumn.MID)
    retire_reason = (from_retirements or {}).get(_RetirementsColumn.RET_REASON)
    retire_change_to = (from_retirements or {}).get(_RetirementsColumn.CHANGE_TO)
    retire_remedy = (from_retirements or {}).get(_RetirementsColumn.REMEDY)

    retire_date = (
        datetime.datetime.strptime(
            from_retirements[_RetirementsColumn.EFFECTIVE], "%Y-%m-%d"
        ).date()
        if from_retirements
        else None
    )

    if from_codes:
        # The ISO 639-3 code is active.
        part2b = from_codes[_CodesColumn.PART2B]
        part2t = from_codes[_CodesColumn.PART2T]
        part1 = from_codes[_CodesColumn.PART1]
        scope = from_codes[_CodesColumn.SCOPE]
        type = from_codes[_CodesColumn.TYPE]
        status = "A"
        ref_name = ref_name
        comment = from_codes[_CodesColumn.COMMENT]

    else:
        # The ISO 639-3 code is retired.
        part2b = None
        part2t = None
        part1 = None
        scope = "I"
        type = None
        status = "R"
        ref_name = ref_name
        comment = None

    language = Language(
        part3=part3,
        part2b=part2b or None,
        part2t=part2t or None,
        part1=part1 or None,
        scope=scope,
        type=type or None,
        status=status,
        name=ref_name,
        comment=comment or None,
        other_names=other_names or None,
        macrolanguage=macrolanguage or None,
        retire_reason=retire_reason or None,
        retire_change_to=retire_change_to or None,
        retire_remedy=retire_remedy or None,
        retire_date=retire_date or None,
    )

    return language


def _get_all_languages() -> dict[str, Language]:
    languages = {}
    for part3 in _PART3_TO_CODES:
        languages[part3] = _get_language(part3)
    for part3 in _PART3_TO_RETIREMENTS:
        languages[part3] = _get_language(part3)
    return languages


_PART3_TO_LANGUAGES: dict[str, Language] = _get_all_languages()

ALL_LANGUAGES: set[Language] = set(_PART3_TO_LANGUAGES.values())
