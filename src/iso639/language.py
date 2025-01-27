"""The Language class."""

from __future__ import annotations

import datetime
import functools
from dataclasses import dataclass

from typing import List, Union, Set, Tuple

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
    # Although Union[..., None] and Optional[...] are equivalent, I prefer Union.
    # Optional simply doesn't sound right, as it would imply that the attribute in
    # question is optional, which it's not.
    # When support for Python 3.9 is dropped, we will switch to the pipe syntax
    # for `... | None`.
    part2b: Union[str, None]
    part2t: Union[str, None]
    part1: Union[str, None]
    scope: str
    type: Union[str, None]
    status: str
    name: str
    comment: Union[str, None]

    # From the "name_index" table
    other_names: Union[List[Name], None]

    # From the "macrolanguages" table
    macrolanguage: Union[str, None]

    # From the "retirements" table
    retire_reason: Union[str, None]
    retire_change_to: Union[str, None]
    retire_remedy: Union[str, None]
    retire_date: Union[datetime.date, None]

    def __hash__(self) -> int:
        return hash(self.part3)

    def __eq__(self, other) -> bool:
        return isinstance(other, Language) and self.part3 == other.part3

    @classmethod
    def match(cls, user_input) -> Language:
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
        # Order of columns to query the data tables.
        # Bias towards (and therefore prioritize) the user input being
        # a language code rather than a language name.
        query_order = (
            _CodesColumn.ID,
            _CodesColumn.PART2B,
            _CodesColumn.PART2T,
            _CodesColumn.PART1,
            _RetirementsColumn.ID,
            _CodesColumn.REF_NAME,
            _NameIndexColumn.PRINT_NAME,
            _NameIndexColumn.INVERTED_NAME,
        )
        return _get_language(user_input, query_order)

    @classmethod
    def from_part3(cls, user_input) -> Language:
        """Return a ``Language`` instance from an ISO 639-3 code."""
        return _get_language(user_input, (_CodesColumn.ID, _RetirementsColumn.ID))

    @classmethod
    def from_part2b(cls, user_input) -> Language:
        """Return a ``Language`` instance from an ISO 639-2 (bibliographic) code."""
        return _get_language(user_input, (_CodesColumn.PART2B,))

    @classmethod
    def from_part2t(cls, user_input) -> Language:
        """Return a ``Language`` instance from an ISO 639-2 (terminological) code."""
        return _get_language(user_input, (_CodesColumn.PART2T,))

    @classmethod
    def from_part1(cls, user_input) -> Language:
        """Return a ``Language`` instance from an ISO 639-1 code."""
        return _get_language(user_input, (_CodesColumn.PART1,))

    @classmethod
    def from_name(cls, user_input) -> Language:
        """Return a ``Language`` instance from an ISO 639-3 reference language name."""
        query_order = (
            _CodesColumn.REF_NAME,
            _NameIndexColumn.PRINT_NAME,
            _NameIndexColumn.INVERTED_NAME,
        )
        return _get_language(user_input, query_order)


@functools.lru_cache()
def _get_language(user_input: str, query_order: Tuple[_COLUMN_TYPE]) -> Language:
    """Create a ``Language`` instance.

    Parameters
    ----------
    user_input : str
        The user-provided language code or name.
    query_order : Tuple[_COLUMN_TYPE]
        A tuple of columns to specify query order.
        A tuple but not a list because this argument needs to be hashable for lru_cache.

    Returns
    -------
    Language

    Raises
    ------
    LanguageNotFoundError
        If `part3` isn't a language name or code
    """
    part3: Union[str, None] = None
    for column in query_order:
        if column == _CodesColumn.ID:
            if user_input in _PART3_TO_CODES:
                part3 = user_input
                break
        elif column == _CodesColumn.PART2B:
            part3 = _PART2B_TO_PART3.get(user_input)
        elif column == _CodesColumn.PART2T:
            part3 = _PART2T_TO_PART3.get(user_input)
        elif column == _CodesColumn.PART1:
            part3 = _PART1_TO_PART3.get(user_input)
        elif column == _RetirementsColumn.ID:
            if user_input in _PART3_TO_RETIREMENTS:
                part3 = user_input
                break
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
        raise LanguageNotFoundError(
            f"{user_input!r} isn't an ISO language code or name"
        )

    from_codes = _PART3_TO_CODES.get(part3)
    from_macrolanguages = _PART3_TO_MACROLANGUAGES.get(part3)
    from_retirements = _PART3_TO_RETIREMENTS.get(part3)

    ref_name = (
        from_codes[_CodesColumn.REF_NAME]
        if from_codes
        else from_retirements[_RetirementsColumn.REF_NAME]  # type: ignore
    )

    other_names: Union[List[Name], None] = []
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


@functools.lru_cache()
def _get_all_languages() -> Set[Language]:
    languages = set()
    for part3 in _PART3_TO_CODES:
        languages.add(_get_language(part3, (_CodesColumn.ID,)))
    for part3 in _PART3_TO_RETIREMENTS:
        languages.add(_get_language(part3, (_RetirementsColumn.ID,)))
    return languages
