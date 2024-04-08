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
from dataclasses import dataclass
from enum import Enum
import sqlite3

class FileMatchState(Enum):
    ''' File matching state enumeration '''
    MISSING = 0
    MATCHED = 1
    MODIFIED = 2

@dataclass
class BasePathEntry:
    """ Class for keeping track of a base path. """
    id: int
    path: str

    def __lt__(self, other):
        return self.id < other.id

class DatabaseLayer:
    """ Database interface layer """
    __slots__ = ["_db_connection"]

    def __init__(self, database : sqlite3.Connection) -> None:
        self._db_connection : sqlite3.Connection = database

    def get_base_paths(self) -> list:
        ''' Get all of the base paths from the database '''

        cursor = self._db_connection.cursor()

        result = cursor.execute("SELECT rowid, path FROM base_path")
        raw_results : list = result.fetchall()

        paths : list[BasePathEntry] = []
        for raw_entry in raw_results:
            entry = BasePathEntry(raw_entry[0], raw_entry[1])
            paths.append(entry)

        return paths


    def verify_file_state(self, base_path_id : int, file : str,
                          file_hash : str) -> FileMatchState:
        ''' Get the state of a file based on name and hash '''

        sql : str = (
            f"SELECT filename, hash FROM file_hash WHERE "
            f"base_path_id = {base_path_id} AND filename='{file}'"
        )

        cursor : sqlite3.Cursor = self._db_connection.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()

        if not row:
            return FileMatchState.MISSING

        hash_from_db : str = row[1]

        return FileMatchState.MATCHED if file_hash == hash_from_db else \
            FileMatchState.MODIFIED

    def add_file_record(self, base_path_id : int, file : str,
                          file_hash : str) -> int:
        ''' Add a new file record into the database '''

        sql : str = ''' INSERT INTO file_hash(base_path_id, filename, hash)
                        VALUES(?,?,?) '''
        sql_values = (base_path_id, file, file_hash)
        cursor : sqlite3.Cursor = self._db_connection.cursor()
        cursor.execute(sql, sql_values)
        self._db_connection.commit()

        return cursor.lastrowid

    def update_file_record(self, base_path_id : int, file : str,
                           file_hash : str) -> None:
        ''' Update file record with a new hash '''

        sql : str = ''' UPDATE file_hash SET hash=?
                        WHERE base_path_id=? AND filename=?'''
        sql_values = (file_hash, base_path_id, file)
        cursor : sqlite3.Cursor = self._db_connection.cursor()
        cursor.execute(sql, sql_values)
        self._db_connection.commit()

        return cursor.lastrowid
