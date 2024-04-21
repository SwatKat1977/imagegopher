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
from typing import Optional
from table_definitions import sql_create_base_path_table, \
                              sql_create_file_hash_table, \
                              sql_create_config_item_table

CONFIG_ITEM_TYPE_BOOLEAN      = 0
CONFIG_ITEM_TYPE_FLOAT        = 1
CONFIG_ITEM_TYPE_INT          = 2
CONFIG_ITEM_TYPE_STRING       = 3
CONFIG_ITEM_TYPE_UNSIGNED_INT = 4

sql_config_item_insert = """
    INSERT INTO config_item(key, value, type) VALUES(?, ?, ?);
    """

class DatabaseBuilder:
    __slots__ = ["_database", "_filename", "_override"]

    def __init__(self, filename : str, override : bool):
        self._database : Optional[sqlite3.Connection] = None
        self._filename : str = filename
        self._override : bool = override

    def open_database(self) -> bool:
        if os.path.isdir(self._filename):
            print("[ERROR] Database specified is a directory!")
            return False

        if os.path.isfile(self._filename):
            if not self._override:
                print("[ERROR] Database specified exists!")
                return False
            else:
                try:
                    os.remove(self._filename)

                except OSError as ex:
                    print(f"Failed to delete old database, reason: {ex}")
                    return False

                print("[WARNING] Database exists and is being overwritten!")

        print(f"[INFO] Creating database file : {self._filename}")

        try:
            self._database = sqlite3.connect(self._filename)
            cursor : sqlite3.Cursor = self._database.cursor()
        except sqlite3.OperationalError as ex:
            print(f"[ERROR[ Database connect failed, reason: {ex}")
            return False

        try:
            cursor.execute("PRAGMA integrity_check")
        except sqlite3.DatabaseError:
            print("[ERROR] Database failed ingrity check!")
            self.close_database()
            return False

        return True

    def close_database(self) -> None:
        self._database.close()

    def create_tables(self) -> bool:
        if not self._create_table("base_path", sql_create_base_path_table):
            return False

        if not self._create_table("file_hash", sql_create_file_hash_table):
           return False

        if not self._create_table("config_item", sql_create_config_item_table):
           return False

        if not self._insert_entry(sql_config_item_insert,
                                  ("last_update", "0",
                                   CONFIG_ITEM_TYPE_INT)) or \
           not self._insert_entry(sql_config_item_insert,
                                  ("scan_interval", "60",
                                   CONFIG_ITEM_TYPE_UNSIGNED_INT)):
            return False

        return True

    def _create_table(self, table_name : str, create_table_sql : str) -> bool:
        try:
            cursor = self._database.cursor()
            cursor.execute(create_table_sql)

        except sqlite3.Error as ex:
            print(f"[ERROR] Failed to create table '{table_name}', reason: {ex}!")
            return False

        print(f"[INFO] Created table '{table_name}'")

        return True

    def _insert_entry(self, sql : str, data : tuple) -> Optional[int]:
        cursor : sqlite3.Cursor = self._database.cursor()

        try:
            cursor.execute(sql, data)
            self._database.commit()

        except sqlite3.Error as ex:
            print(f"[ERROR] SQL insert statement failed, reason: {ex}!")
            return None

        return cursor.lastrowid

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

    db_builder = DatabaseBuilder(database_file, override_existing)

    if not db_builder.open_database():
        return

    if not db_builder.create_tables():
       db_builder.close_database()
       print("[ERROR] Database table creation failed, aborting!")
       return

    print("[INFO] Database successfully created!")
    db_builder.close_database()

if __name__ == '__main__':
    main(sys.argv[1:])
