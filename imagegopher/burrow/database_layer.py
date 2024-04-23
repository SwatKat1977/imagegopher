'''
Copyright 2014-2023 Integrated Test Management Suite

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
import logging
import sqlite3
from time import time
from typing import Optional

SQL_INSERT_BASE_PATH : str = "INSERT INTO base_path(path) VALUES(?)"

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

    def update_config_item_scan_interval(self, interval : int) -> bool:
        ''' Update the configuration item 'Scan Interval '''

        sql : str = 'UPDATE config_item set value=? WHERE key="scan_interval"'

        try:
            self._sql_update(sql, (interval,))

        except ValueError as ex:
            self._logger.error(
                f"Update 'scan_interval' config option failed, reason: {ex}!")
            return False

        return self._update_last_update()

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
