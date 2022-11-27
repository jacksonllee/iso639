# python-iso639

[![PyPI version](https://badge.fury.io/py/python-iso639.svg)](https://pypi.org/project/python-iso639/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/python-iso639.svg)](https://pypi.org/project/python-iso639/)
[![CircleCI Builds](https://circleci.com/gh/jacksonllee/iso639.svg?style=shield)](https://circleci.com/gh/jacksonllee/iso639)

`python-iso639` is a Python package for accessing ISO 639 language codes, names, and
other associated information.

Current features:

* A representation of languages mapped across ISO 639-1, 639-2, and 639-3.
* Functionality to "guess" what a language is for a given
  unknown language code or name.

## Installation

```bash
pip install python-iso639
```

## Usage

`python-iso639` revolves around a `Language` class.
Instances of `Language` have attributes and methods that you will find useful.

Note that while the package name registered on PyPI is `python-iso639`,
the actual import name during runtime is `iso639`
(which means you should do `import iso639` in your Python code).

### Creating `Language` Instances

Create a `Language` instance by one of the methods.

#### `from_part3`, with an ISO 639-3 code

```python
>>> import iso639
>>> lang1 = iso639.Language.from_part3('fra')
>>> type(lang1)
<class 'iso639.language.Language'>
>>> lang1
Language(part3='fra', part2b='fre', part2t='fra', part1='fr', scope='I', type='L', name='French', comment=None, other_names=None, macrolanguage=None, retire_reason=None, retire_change_to=None, retire_remedy=None, retire_date=None)
```

#### From Another ISO 639 Code Set or a Reference Name

```python
>>> lang2 = iso639.Language.from_part2b('fre')  # ISO 639-2 (bibliographic)
>>> lang3 = iso639.Language.from_part2t('fra')  # ISO 639-2 (terminological)
>>> lang4 = iso639.Language.from_part1('fr')  # ISO 639-1
>>> lang5 = iso639.Language.from_name('French')  # ISO 639-3 reference language name
```

#### A `LanguageNotFoundError` is Raised for Invalid Inputs

```python
>>> iso639.Language.from_part3('Fra')  # The user input is case-sensitive!
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
LanguageNotFoundError: 'Fra' isn't an ISO language code or name
>>>
>>> iso639.Language.from_name("unknown language")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
LanguageNotFoundError: 'unknown language' isn't an ISO language code or name
```

### Accessing Attributes

```python
>>> lang1
Language(part3='fra', part2b='fre', part2t='fra', part1='fr', scope='I', type='L', name='French', comment=None, other_names=None, macrolanguage=None, retire_reason=None, retire_change_to=None, retire_remedy=None, retire_date=None)
>>> lang1.part3
'fra'
>>> lang1.name
'French'
```

### Comparison

```python
>>> lang1 == lang2 == lang3 == lang4 == lang5  # All are French
True
>>> lang6 = iso639.Language.from_part3('spa')  # Spanish
>>> lang1 == lang6  # French vs. Spanish
False
>>> 'French' == lang1.name == lang2.name == lang3.name == lang4.name == lang5.name
True
>>> lang6.name
'Spanish'
```

### Guess a Language: Classmethod `match`

You don't know which code set or name your input is from?
Use the `match` classmethod:

```python
>>> lang1 = iso639.Language.match('fra')
>>> lang2 = iso639.Language.match('fre')
>>> lang3 = iso639.Language.match('fr')
>>> lang4 = iso639.Language.match('French')
>>> lang1 == lang2 == lang3 == lang4
True
```

The classmethod `match` is particularly useful for consistently
accessing a specific attribute from unknown inputs, e.g., the ISO 639-3 code.

```python
>>> 'fra' == lang1.part3 == lang2.part3 == lang3.part3 == lang4.part3
True
```

If there's no match, a `LanguageNotFoundError` is raised,
which you may want to catch:

```python
>>> try:
...     lang = iso639.Language.match('not gonna find a match')
... except iso639.LanguageNotFoundError:
...     print("no match found!")
... 
no match found!
```

### Macrolanguages and Alternative Names

```python
>>> language = iso639.Language.match('yue')
>>> language.name
'Yue Chinese'  # also commonly known as Cantonese
>>> language.macrolanguage
'zho'  # Chinese
>>> language.other_names
[Name(print='Yue Chinese', inverted='Chinese, Yue')]
>>> for name in language.other_names:
...     print(f'{name.print} | {name.inverted}')
...
Yue Chinese | Chinese, Yue
```

### Retired Language Codes:

```python
>>> language = iso639.Language.match('bvs')
>>> language.part3
'bvs'
>>> language.name
'Belgian Sign Language'
>>> language.status
'R'  # (R)etired
>>> language.retire_reason
'S'  # (S)plit
>>> language.retire_change_to is None
True
>>> language.retire_remedy
'Split into Langue des signes de Belgique Francophone [sfb], and Vlaamse Gebarentaal [vgt]'
>>> language.retire_date
datetime.date(2007, 7, 18)
```

## Into the Weeds

### Attributes of a `Language` Instance

A `Language` instance has the following attributes:

| Attribute          | Data type       | Can it be `None`? | Description                                                                                                           |
|--------------------|-----------------|-------------------|-----------------------------------------------------------------------------------------------------------------------|
| `part3`            | `str`           | ✗                 | ISO 639-3 code                                                                                                        |
| `part2b`           | `str`           | ✓                 | ISO 639-2 code (bibliographic)                                                                                        |
| `part2t`           | `str`           | ✓                 | ISO 639-2 code (terminological)                                                                                       |
| `part1`            | `str`           | ✓                 | ISO 639-1 code                                                                                                        |
| `scope`            | `str`           | ✗                 | One of {(I)ndividual, (M)acrolanguage, (S)pecial}                                                                     |
| `type`             | `str`           | ✓                 | One of {(A)ncient, (C)onstructed, (E)xtinct, (H)istorical, (L)iving, (S)pecial} [1]                                   |
| `status`           | `str`           | ✗                 | One of {(A)ctive, (R)etired}, describing the ISO 639-3 code                                                           |
| `name`             | `str`           | ✗                 | Reference language name in ISO 639-3                                                                                  |
| `comment`          | `str`           | ✓                 | Comment from ISO 639-3                                                                                                |
| `other_names`      | `List[Name]`    | ✓                 | Other print and inverted names [2]                                                                                    |
| `macrolanguage`    | `str`           | ✓                 | Macrolanguage                                                                                                         |
| `retire_reason`    | `str`           | ✓                 | Retirement reason, one of {(C)hange, (D)uplicate, (N)on-existent, (S)plit, (M)erge}                                   |
| `retire_change_to` | `str`           | ✓                 | ISO 639-3 code to which this language can be changed, if retirement reason is one of {(C)hange, (D)uplicate, (M)erge} |
| `retire_remedy`    | `str`           | ✓                 | Instructions for updating this retired language code                                                                  |
| `retire_date`      | `datetime.date` | ✓                 | The date the retirement became effective                                                                              |

[1] If the ISO 639-3 code is retired, then the `type` attribute is `None`,
    because its value is not clearly discernible from the SIL data source.

[2] A `Name` instance has the attributes `print` and `inverted`,
    for the print name and inverted name, respectively.
    If reference name, print name, and inverted name are all the same, then
    that particular (print name, inverted name) pair is excluded from
    the `other_names` attribute.
    For example, for Spanish (ISO 639-3: spa), one (print name, inverted name)
    pair is (Spanish, Spanish) from the SIL data source, but this pair is
    excluded from its list of `other_names`.

### How `Language.match` Matches the Language

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

Only exact matching is done (there's no fuzzy string matching of any sort).
As soon as a match is found, `Language.match` returns a `Language` instance.
If there isn't a match, a `LanguageNotFoundError` is raised.

### `Language` is a dataclass

The `Language` class is a dataclass.
All functionality of
[dataclases](https://docs.python.org/3/library/dataclasses.html)
applies to `Language` and its instances,
e.g., [`dataclasses.asdict`](https://docs.python.org/3/library/dataclasses.html#dataclasses.asdict):

```python
>>> import dataclasses, iso639
>>> language = iso639.Language.match('fra')
>>> dataclasses.asdict(language)
{'part3': 'fra', 'part2b': 'fre', 'part2t': 'fra', 'part1': 'fr', 'scope': 'I', 'type': 'L', 'status': 'A', 'name': 'French', 'comment': None, 'other_names': None, 'macrolanguage': None, 'retire_reason': None, 'retire_change_to': None, 'retire_remedy': None, 'retire_date': None}
```

### Constants

* `DATA_LAST_UPDATED`: The release date of the included language code data from SIL

    ```python
    >>> import iso639
    >>> iso639.DATA_LAST_UPDATED
    datetime.date(2022, 3, 11)
    ```

* `ALL_LANGUAGES`: The list of all `Language` objects based on the included language code data

    ```python
    >>> import iso639
    >>> type(iso639.ALL_LANGUAGES)
    <class 'list'>
    >>> len(iso639.ALL_LANGUAGES)
    7910
    >>> iso639.ALL_LANGUAGES[0]
    Language(part3='aaa', scope='I', type='L', status='A', name='Ghotuo', ...)
    ```

## Links

* Author: [Jackson L. Lee](https://jacksonllee.com)
* Source code: https://github.com/jacksonllee/iso639

## License and Data Source

The `python-iso639` code is released under an Apache 2.0 license.
Please see [LICENSE.txt](https://github.com/jacksonllee/iso639/blob/main/LICENSE.txt)
for details.

The data source that backs this package is the
[language code tables published by SIL](https://iso639-3.sil.org/code_tables/download_tables).
Note that SIL resources have their [terms of use](https://www.sil.org/terms-use).

## Why Another ISO 639 Package?

Both packages [iso639](https://pypi.org/project/iso639/)
and [iso-639](https://pypi.org/project/iso-639/) exist on PyPI.
However, as of this writing (May 2022), they were last updated in 2016 and don't seem to be maintained anymore
for updating the language codes.
[pycountry](https://pypi.org/project/pycountry/) is a great package,
but what if you want a more lightweight package with just the language codes only and not the other stuff? :-)

If you ever notice that the upstream ISO 639-3 tables from SIL have been updated
and yet this package isn't using the latest data,
please ping me by [opening a GitHub issue](https://github.com/jacksonllee/iso639/issues).
