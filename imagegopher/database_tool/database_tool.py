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
import sqlite3
import sys
import typing


class DatabaseBuilder:
    __slots__ = ["_database", "_filename", "_override"]

    def __init__(self, filename : str, override : bool):
        self._database: typing.Optional[sqlite3.Connection] = None
        self._filename: str = filename
        self._override: bool = override


def display_usage() -> None:
    print('gatherer_db_tool -d <database> -o')
    print(" -h : Display this help")
    print(" -d : Database file")
    print(" -o : Override database file write if exists (DANGEROUS)")


def main(argv : list) -> None:

    database_file : Optional[str] = None
    override_existing : bool = False

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


if __name__ == '__main__':
    main(sys.argv[1:])
