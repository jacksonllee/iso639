#!/usr/bin/env python3

"""A script to create or update `languages.db`.

The source data tables are the four `.tab` files (codes, name index, macrolanguages,
and retirements) downloadable from https://iso639-3.sil.org/code_tables/download_tables.

To update the existing `languages.db`, run `python create_languages_db.py --overwrite`.
"""

import argparse
import csv
import logging
import os
import shutil
import sqlite3
import tempfile

try:
    import requests
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "The package `requests` isn't installed. "
        'To install it, run `pip install -e ".[dev]"`.'
    )

# These default filenames are exactly those from SIL as of April 2024.
_DEFAULT_FILENAMES = {
    "codes": "iso-639-3.tab",
    "name_index": "iso-639-3_Name_Index.tab",
    "macrolanguages": "iso-639-3-macrolanguages.tab",
    "retirements": "iso-639-3_Retirements.tab",
}

_LANGUAGES_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    "src",
    "iso639",
    "languages.db",
)


def get_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default="https://iso639-3.sil.org/sites/iso639-3/files/downloads",
        help="The base URL to the various tab-separated value files",
    )
    parser.add_argument(
        "--codes",
        default=_DEFAULT_FILENAMES["codes"],
        help="TSV base filename for ISO 639-3 language code chart",
    )
    parser.add_argument(
        "--name-index",
        default=_DEFAULT_FILENAMES["name_index"],
        help="TSV base filename for ISO 639-3 name index chart",
    )
    parser.add_argument(
        "--macrolanguages",
        default=_DEFAULT_FILENAMES["macrolanguages"],
        help="TSV base filename for ISO 639-3 macrolanguage chart",
    )
    parser.add_argument(
        "--retirements",
        default=_DEFAULT_FILENAMES["retirements"],
        help="TSV base filename for ISO 639-3 retired language code chart",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help=(
            "Apply this flag to overwrite the existing languages.db "
            "and create a new one"
        ),
    )
    args = parser.parse_args()
    return args


def get_conn(overwrite: bool) -> sqlite3.Connection:
    languages_db_exists = os.path.exists(_LANGUAGES_DB_PATH)
    if languages_db_exists and not overwrite:
        raise ValueError(
            f"languages.db already exists at {_LANGUAGES_DB_PATH}. "
            "To overwrite it and create a new one, apply the --overwrite flag."
        )
    elif languages_db_exists:
        logging.info(
            f"languages.db already exists at {_LANGUAGES_DB_PATH}. "
            "This script is overwriting it by creating a new one."
        )
        os.remove(_LANGUAGES_DB_PATH)
    else:
        logging.info(
            f"languages.db doesn't yet exist at {_LANGUAGES_DB_PATH}. "
            "This script is creating a new one."
        )
    return sqlite3.connect(_LANGUAGES_DB_PATH)


def download_file(base_url: str, tsv_filename: str) -> str:
    tsv_path = os.path.join(tempfile.mkdtemp(), tsv_filename)
    url = f"{base_url.rstrip('/')}/{tsv_filename}"
    with open(tsv_path, "wb") as f, requests.get(url, stream=True) as r:
        shutil.copyfileobj(r.raw, f)
    logging.info("downloaded %r to file %r", url, tsv_path)
    return tsv_path


def _construct_table(*, conn, tsv_path, table_name, create_table, n_columns) -> None:
    """A general function to create a table at the _SQLITE_CONN connection.

    Parameters
    ----------
    conn : sqlite3.Connection
    tsv_path : str
        File path of the input tab-separated value file.
    table_name : str
        SQL table name.
    create_table : str
        SQL statement that creates the table.
    n_columns : int
        Number of columns in the table to be created.
    """
    c = conn.cursor()
    c.execute(create_table)
    insert_statement = f"INSERT INTO {table_name} VALUES ({','.join('?' * n_columns)})"
    with open(tsv_path, newline="") as tsv_file:
        tsv_reader = csv.DictReader(tsv_file, delimiter="\t")
        rows = []
        for i, row in enumerate(tsv_reader, 1):
            row_tuple = tuple(x or None for x in row.values())
            rows.append(row_tuple)

            if i % 256 == 0:
                c.executemany(insert_statement, rows)
                rows = []

        if rows:
            c.executemany(insert_statement, rows)

    conn.commit()


def construct_codes_table(
    conn: sqlite3.Connection, base_url: str, tsv_filename: str
) -> None:
    # CREATE TABLE statement from:
    # https://iso639-3.sil.org/code_tables/download_tables#639-3%20Code%20Set
    create_table = """
        CREATE TABLE codes (
            Id      char(3) NOT NULL,  -- The three-letter 639-3 identifier
            Part2B  char(3) NULL,      -- Equivalent 639-2 identifier of the bibliographic applications
                                       -- code set, if there is one
            Part2T  char(3) NULL,      -- Equivalent 639-2 identifier of the terminology applications code
                                       -- set, if there is one
            Part1   char(2) NULL,      -- Equivalent 639-1 identifier, if there is one
            Scope   char(1) NOT NULL,  -- I(ndividual), M(acrolanguage), S(pecial)
            Type    char(1) NOT NULL,  -- A(ncient), C(onstructed),
                                       -- E(xtinct), H(istorical), L(iving), S(pecial)
            Ref_Name   varchar(150) NOT NULL,   -- Reference language name
            Comment    varchar(150) NULL)       -- Comment relating to one or more of the columns
        """  # noqa: E501
    tsv_path = download_file(base_url, tsv_filename)
    _construct_table(
        conn=conn,
        tsv_path=tsv_path,
        table_name="codes",
        create_table=create_table,
        n_columns=8,
    )


def construct_name_index_table(
    conn: sqlite3.Connection, base_url: str, tsv_filename: str
) -> None:
    # CREATE TABLE statement from:
    # https://iso639-3.sil.org/code_tables/download_tables#Language%20Names%20Index
    create_table = """
        CREATE TABLE name_index (
            Id             char(3)     NOT NULL,  -- The three-letter 639-3 identifier
            Print_Name     varchar(75) NOT NULL,  -- One of the names associated with this identifier
            Inverted_Name  varchar(75) NOT NULL)  -- The inverted form of this Print_Name form
        """  # noqa: E501
    tsv_path = download_file(base_url, tsv_filename)
    _construct_table(
        conn=conn,
        tsv_path=tsv_path,
        table_name="name_index",
        create_table=create_table,
        n_columns=3,
    )


def construct_macrolanguages_table(
    conn: sqlite3.Connection, base_url: str, tsv_filename: str
) -> None:
    # CREATE TABLE statement from:
    # https://iso639-3.sil.org/code_tables/download_tables#Macrolanguage%20mappings
    create_table = """
        CREATE TABLE macrolanguages (
            M_Id      char(3) NOT NULL,   -- The identifier for a macrolanguage
            I_Id      char(3) NOT NULL,   -- The identifier for an individual language
                                          -- that is a member of the macrolanguage
            I_Status  char(1) NOT NULL)   -- A (active) or R (retired) indicating the
                                          -- status of the individual code element
        """  # noqa: E501
    tsv_path = download_file(base_url, tsv_filename)
    _construct_table(
        conn=conn,
        tsv_path=tsv_path,
        table_name="macrolanguages",
        create_table=create_table,
        n_columns=3,
    )


def construct_retirements_table(
    conn: sqlite3.Connection, base_url: str, tsv_filename: str
) -> None:
    # CREATE TABLE statement from:
    # https://iso639-3.sil.org/code_tables/download_tables#Deprecated%20Code%20Mappings
    create_table = """
        CREATE TABLE retirements (
            Id          char(3)      NOT NULL,     -- The three-letter 639-3 identifier
            Ref_Name    varchar(150) NOT NULL,     -- reference name of language
            Ret_Reason  char(1)      NOT NULL,     -- code for retirement: C (change), D (duplicate),
                                                   -- N (non-existent), S (split), M (merge)
            Change_To   char(3)      NULL,         -- in the cases of C, D, and M, the identifier
                                                   -- to which all instances of this Id should be changed
            Ret_Remedy  varchar(300) NULL,         -- The instructions for updating an instance
                                                   -- of the retired (split) identifier
            Effective   date         NOT NULL)     -- The date the retirement became effective
        """  # noqa: E501
    tsv_path = download_file(base_url, tsv_filename)
    _construct_table(
        conn=conn,
        tsv_path=tsv_path,
        table_name="retirements",
        create_table=create_table,
        n_columns=6,
    )


def main():
    logging.basicConfig(format="%(levelname)s: %(message)s", level="INFO")
    args = get_cli_args()
    conn = get_conn(args.overwrite)
    construct_codes_table(conn, args.base_url, args.codes)
    construct_name_index_table(conn, args.base_url, args.name_index)
    construct_macrolanguages_table(conn, args.base_url, args.macrolanguages)
    construct_retirements_table(conn, args.base_url, args.retirements)
    logging.info("New languages.db created!")


if __name__ == "__main__":
    main()
