# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

The version number is based on [calendar versioning](https://calver.org/).
The specific format is `YYYY.(M)M.(D)D`,
where the month and day may be single-digit because Python doesn't allow zero-padded
major/minor/micro version numbers like `05` (it'd have to be just `5`).

## [Unreleased]

### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security

## [2022.11.27]

### Added
* Defined the `LanguageNotFoundError` exception.
* Added support for Python 3.11.

### Changed
* If the `Language` class methods `match`, `from_part3`, etc. receive an invalid
  input language code or name, a `LanguageNotFoundError` is now raised.
  (Previously, `None` was returned with no exception raised.)

### Removed
* Dropped support for Python 3.7.

## [2022.9.17]

### Added
* Added constants `DATA_LAST_UPDATED` and `ALL_LANGUAGES`.

## [2022.5.16]

### Fixed
* Corrected repo name in package metadata and documentation.

## [2022.5.15]

* First release!
