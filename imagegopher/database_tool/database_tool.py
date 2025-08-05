"""
This source file is part of Image Gopher
For the latest info, see https://github.com/SwatKat1977/imagegopher

Copyright 2025 Image Gopher Development Team

This program is free software : you can redistribute it and /or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.If not, see < https://www.gnu.org/licenses/>.
"""
import getopt
import os
import sys
import typing
from shared.base_sqlite_interface import BaseSqliteInterface, \
                                         SqliteInterfaceException
import table_definitions as tables


class DatabaseBuilder:
    __slots__ = ["_database", "_filename", "_override"]

    def __init__(self, filename : str, override : bool):
        self._database: typing.Optional[BaseSqliteInterface] = None
        self._filename: str = filename
        self._override: bool = override

    def is_valid_database(self) -> bool:
        if os.path.isdir(self._filename):
            print("[ERROR] Database specified is a directory!")
            return False

        if os.path.isfile(self._filename):
            if not self._override:
                print("[ERROR] Database specified exists!")
                return False

            try:
                os.remove(self._filename)

            except OSError as ex:
                print(f"Failed to delete old database, reason: {ex}")
                return False

            print("[WARNING] Database exists and is being overwritten!")

        self._database = BaseSqliteInterface(self._filename)
        return True

    def create_tables(self) -> bool:
        if not self._create_table("base_path",
                                  tables.sql_create_base_path_table):
            return False

        if not self._create_table("file_hash",
                                  tables.sql_create_file_hash_table ):
            return False

        try:
            self._database.run_query(tables.sql_create_index_for_file_hash,
                                     commit=True)

        except SqliteInterfaceException as ex:
            print("[ERROR] Failed to create index for file_hash, "
                  f"reason: {ex}")
            return False

        return True

    def _create_table(self, table_name: str, create_table_sql: str) -> bool:
        try:
            self._database.create_table(create_table_sql, table_name)

        except SqliteInterfaceException as ex:
            print(f"[ERROR] Failed to create table '{table_name}', reason: {ex}!")
            return False

        print(f"[INFO] Created table '{table_name}'")

        return True


def display_usage() -> None:
    print('gatherer_db_tool -d <database> -o')
    print(" -h : Display this help")
    print(" -d : Database file")
    print(" -o : Override database file write if exists (DANGEROUS)")


def main(argv : list) -> None:

    database_file: typing.Optional[str] = None
    override_existing: bool = False

    try:
        opts, _ = getopt.getopt(argv,"hd:o",["database="])

        for opt, arg in opts:
            if opt == "-h":
                display_usage()
                return

            elif opt in ("-d", "--database"):
                database_file = arg

            elif opt == "-o":
                override_existing = True

        if not database_file:
            print("[ERROR] Not database has been specified!")
            return

    except getopt.GetoptError:
        display_usage()
        return

    db_builder = DatabaseBuilder(database_file, override_existing)

    if not db_builder.is_valid_database():
        return

    if not db_builder.create_tables():
        return

    print("[INFO] Database created...")


if __name__ == '__main__':
    main(sys.argv[1:])
