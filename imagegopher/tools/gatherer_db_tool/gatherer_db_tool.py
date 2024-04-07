"""
This source file is part of Image Gopher
For the latest info, see https://github.com/SwatKat1977/imagegopher

Copyright 2024 Image Gopher Development Team

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
import sqlite3
import sys

def display_usage() -> None:
    print('gatherer_db_tool -d <database> -o')
    print(" -h : Display this help")
    print(" -d : Database file")
    print(" -o : Override database file write if exists (DANGEROUS)")

def main(argv : list) -> None:

    database_file : str = None
    override_existing : bool = False

    try:
        opts, args = getopt.getopt(argv,"hd:o",["database="])

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

    if os.path.isdir(database_file):
        print("[ERROR] Database specified is a directory!")
        return

    if os.path.isfile(database_file):
        if not override_existing:
            print("[ERROR] Database specified exists!")
            return
        else:
            print("[WARNING] Database exists and is being overwritten!")

    print(f"[INFO] Creating database file : {database_file}")

    try:
        db_connection = sqlite3.connect(database_file)
        db_cursor = db_connection.cursor()
    except sqlite3.OperationalError as ex:
        print(f"[ERROR[ Database connect failed, reason: {ex}")
        return

    try:
        db_cursor.execute("PRAGMA integrity_check")
    except sqlite3.DatabaseError:
        print("[ERROR] Database failed ingrity check!")
        db_connection.close()
        return

    print("[INFO] Database successfully created!")

if __name__ == '__main__':
    main(sys.argv[1:])
