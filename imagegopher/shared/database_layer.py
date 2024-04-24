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
import logging
import sqlite3
from time import time
from typing import Optional

SQL_INSERT_BASE_PATH : str = "INSERT INTO base_path(path) VALUES(?)"

class FileMatchState(Enum):
    ''' File matching state enumeration '''
    MISSING = 0
    MATCHED = 1
    MODIFIED = 2

@dataclass
class BasePathEntry:
    """ Class for keeping track of a base path. """
    row_id: int
    path: str

    def __lt__(self, other):
        return self.row_id < other.row_id

class DatabaseLayer:
    """ Database interface layer """
    __slots__ = ["_db_connection", "_logger"]

    def __init__(self, logger : logging.Logger,
                 database : sqlite3.Connection) -> None:
        self._db_connection : sqlite3.Connection = database
        self._logger = logger.getChild(__name__)

    def valid_base_path(self, base_path : str) -> bool:
        ''' Check if base path exists already '''
        cursor = self._db_connection.cursor()

        try:
            result = cursor.execute("SELECT rowid FROM base_path WHERE PATH = ?",
                                    (base_path,))

        except sqlite3.Error as ex:
            self._logger.error(f"SQL select statement failed, reason: {ex}!")
            return False

        raw_results : list = result.fetchall()
        return True if raw_results else False

    def add_base_path(self, base_path : str) -> bool:
        ''' Add new base path to the database '''

        if self.valid_base_path(base_path):
            raise ValueError("Base path already exists!")

        try:
            self._sql_insert(SQL_INSERT_BASE_PATH, (base_path,))

        except ValueError as ex:
            self._logger.error(f"SQL insert statement failed, reason: {ex}!")
            return False

        return True

    def get_config_item_scan_interval(self) -> int | None:
        ''' Get the configuration item 'Scan Interval' '''

        cursor = self._db_connection.cursor()
        sql : str = 'SELECT value FROM config_item WHERE key="scan_interval"'

        result = cursor.execute(sql)
        results : list = result.fetchall()

        if not results:
            self._logger.error("Cannot get 'scan_interval' config option")
            return None

        return int(results[0][0])

    def update_config_item_scan_interval(self, interval : int) -> bool:
        ''' Update the configuration item 'Scan Interval' '''

        sql : str = 'UPDATE config_item set value=? WHERE key="scan_interval"'

        try:
            self._sql_update(sql, (interval,))

        except ValueError as ex:
            self._logger.error(
                f"Update 'scan_interval' config option failed, reason: {ex}!")
            return False

        return self._update_last_update()

    def get_config_item_last_update(self) -> int | None:
        ''' Get the configuration item 'last update' '''

        cursor = self._db_connection.cursor()
        sql : str = 'SELECT value FROM config_item WHERE key="last_update"'

        result = cursor.execute(sql)
        results : list = result.fetchall()

        if not results:
            self._logger.error("Cannot get 'last_update' config option")
            return None

        return int(results[0][0])

    def update_config_item_library_hash(self, new_hash : str) -> bool:
        ''' Update the configuration item 'Library Hash' '''

        sql : str = 'UPDATE config_item set value=? WHERE key="library_hash"'

        try:
            self._sql_update(sql, (new_hash,))

        except ValueError as ex:
            self._logger.error(
                f"Update 'library_hash' config option failed, reason: {ex}!")
            return False

    def get_config_item_library_hash(self) -> str | None:
        ''' Get the configuration item 'library hash' '''

        cursor = self._db_connection.cursor()
        sql : str = 'SELECT value FROM config_item WHERE key="library_hash"'

        result = cursor.execute(sql)
        results : list = result.fetchall()

        if not results:
            self._logger.error("Cannot get 'library_hash' config option")
            return None

        return results[0][0]

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

    def _sql_insert(self, sql : str, data : tuple) -> Optional[int]:
        cursor : sqlite3.Cursor = self._db_connection.cursor()

        try:
            cursor.execute(sql, data)
            self._db_connection.commit()

        except sqlite3.Error as ex:
            raise ValueError(
                f"[ERROR] SQL insert statement failed, reason: {ex}!") from ex

        return cursor.lastrowid

    def _sql_update(self, sql : str, data : tuple) -> None:
        cursor : sqlite3.Cursor = self._db_connection.cursor()

        try:
            cursor.execute(sql, data)
            self._db_connection.commit()

        except sqlite3.Error as ex:
            raise ValueError(
                f"[ERROR] SQL update statement failed, reason: {ex}!") from ex

    def _update_last_update(self) -> bool:
        sql : str = 'UPDATE config_item set value=? WHERE key="last_update"'
        now : int = int(time())

        try:
            self._sql_update(sql, (now,))

        except ValueError as ex:
            self._logger.error(
                f"Update 'last update' config option failed, reason: {ex}!")
            return False

        return True
