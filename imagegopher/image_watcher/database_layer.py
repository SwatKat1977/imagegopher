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
import logging
import typing
from service_health_enum import ComponentDegradationLevel
from state_object import StateObject
from shared.base_sqlite_interface import BaseSqliteInterface, \
                                         SqliteInterfaceException


class DatabaseLayer(BaseSqliteInterface):
    """
    A high-level interface for interacting with the SQLite database layer of
    the application, providing safe methods for inserting, querying, and
    validating data with robust error handling and logging.

    This class extends `BaseSqliteInterface` and adds domain-specific logic
    such as managing base paths, logging SQL errors, and updating application
    state when database failures occur.

    Attributes:
        _logger (logging.Logger): Logger instance scoped to this class for
                                  detailed error tracking.
        _state_object (StateObject): Application state object for setting
                                     database health indicators.
    """
    __slots__ = ["_logger", "_state_object"]

    def __init__(self,
                 logger: logging.Logger,
                 db_filename: str,
                 state_object: StateObject) -> None:
        super().__init__(db_filename)
        self._logger = logger.getChild(__name__)
        self._state_object: StateObject = state_object

    def add_base_path(self, base_path: str) -> typing.Optional[int]:
        """ Add new base path to the database """

        query: str = "INSERT INTO base_path(path) VALUES(?)"

        row_id: int = self.get_base_path_id(base_path)

        # Check to see if get_base_path_id failed to get id.
        if row_id is None:
            return None

        # Base path already exists.
        if not row_id:
            return 0

        new_row_id: typing.Optional[int] = self._safe_insert_query(
            query,
            (base_path,),
            error_message="Unable to add new base path",
            log_level=logging.CRITICAL
        )

        if new_row_id is None:
            return None

        return new_row_id

    def add_file_entry(self, parameters: tuple):
        """
        Insert a new file entry into the database.

        Args:
            parameters (tuple): A tuple containing
                (base_path_id, subdir, filename, file_hash, last_modified).

        Returns:
            Optional[int]: The row ID of the inserted file entry if successful,
                           otherwise None.
        """
        base_path_id, subdir, filename, file_hash, last_modified = parameters

        query: str = ("INSERT INTO file_entry(base_path_id, subdir, filename, "
                      "hash, last_modified) VALUES(?,?,?,?,?)")
        params = (base_path_id, subdir, filename, file_hash, last_modified)

        row_id: typing.Optional[int] = self._safe_insert_query(
            query,
            params,
            error_message="Unable to add new file entry",
            log_level=logging.CRITICAL
        )

        return row_id

    def get_base_path_id(self, base_path: str) -> typing.Optional[int]:
        """
        Retrieve the ID of the base path if it exists.

        Args:
            base_path (str): The base path string to search for.

        Returns:
            Optional[int]: The ID of the base path if found, else None.
        """
        query: str = "SELECT id FROM base_path WHERE PATH = ?"

        row = self._safe_query(query,
                               (base_path,),
                               "Unable to check if base path exists",
                               log_level=logging.CRITICAL,
                               fetch_one=True)

        if row is None:
            return None

        return 0 if not row else row

    def get_base_paths(self) -> list:
        """
        Retrieve all base path records from the database.

        Returns:
            list: A list of tuples, where each tuple contains:
                - id (int): The base path ID.
                - path (str): The base path string.

        Notes:
            This method queries the `base_path` table for all records.
            If the query fails, an empty list may be returned depending on
            `_safe_query`'s implementation. Errors are logged at CRITICAL level.
        """
        query: str = "SELECT id, path FROM base_path"

        rows = self._safe_query(query,
                                (),
                                "Unable to get all base paths",
                                log_level=logging.CRITICAL)

        return rows

    def get_file_entries_for_directory(self, base_path: str, sub_dir: str) -> list:
        """
        Retrieve all file entries for a specific directory.

        Args:
            base_path (str): The root path associated with the base path record.
            sub_dir (str): The subdirectory under the base path to filter by.

        Returns:
            list: A list of matching file entry records, or an empty list if none are found.

        Notes:
            This method performs a SQL join between `file_entry` and `base_path`
            to match entries based on the given base path and subdirectory.
            Errors are logged at CRITICAL level, and an empty list is returned
            if the query fails.
        """
        sql: str = ("SELECT file_entry.* "
                    "FROM file_entry "
                    "JOIN base_path ON file_entry.base_path_id = base_path.id "
                    "WHERE base_path.path = ? AND file_entry.subdir = ?")

        return self._safe_query(
            sql,
            (base_path, sub_dir),
            error_message="Unable to get file entries for directory",
            log_level=logging.CRITICAL
        )

    def _safe_query(self,
                    query: str,
                    values: tuple | None,
                    error_message: str,
                    log_level: int = logging.CRITICAL,
                    fetch_one: bool = False,
                    commit: bool = False
                    ) -> typing.Optional[typing.Any]:
        # pylint: disable=too-many-arguments, too-many-positional-arguments
        """
        Safely execute a database query with standardized exception handling,
        logging, and database health state updates.

        Args:
            query (str): SQL query string to execute.
            values (tuple): Parameter values for the query.
            error_message (str): Description for the logger on failure.
            log_level (int): Logging level (e.g., logging.CRITICAL).
            fetch_one (bool): If True, fetch only one result. Default is False.
            commit (bool): If True, commit changes (for INSERT/UPDATE/DELETE).

        Returns:
            Optional[Any]: Query result (single row, list of rows, or None).
        """
        try:
            return self.run_query(query, values, fetch_one=fetch_one, commit=commit)

        except SqliteInterfaceException as ex:
            self._logger.log(log_level, "%s, reason: %s", error_message, str(ex))
            self._state_object.database_health = ComponentDegradationLevel.FULLY_DEGRADED
            self._state_object.database_health_state_str = "Fatal SQL failure"
            return None

    def _safe_insert_query(self,
                           query: str,
                           values: tuple,
                           error_message: str,
                           log_level: int = logging.CRITICAL
                           ) -> typing.Optional[int]:
        """
        Safely execute an INSERT query and return the last inserted row ID.

        Args:
            query (str): The INSERT SQL statement.
            values (tuple): Parameters for the query.
            error_message (str): Description for the logger on failure.
            log_level (int): Logging level (e.g., logging.CRITICAL).

        Returns:
            Optional[int]: ID of the last inserted row, or None on failure.
        """

        try:
            return self.insert_query(query, values)

        except SqliteInterfaceException as ex:
            self._logger.log(log_level, "%s, reason: %s", error_message, str(ex))
            self._state_object.database_health = ComponentDegradationLevel.FULLY_DEGRADED
            self._state_object.database_health_state_str = "Fatal SQL failure"
            return None

    def _safe_bulk_insert(self,
                          query: str,
                          value_sets: list[tuple],
                          error_message: str,
                          log_level: int = logging.CRITICAL) -> bool:
        """
        Safely execute a bulk INSERT operation with standardized exception
        handling.

        Args:
            query (str): SQL INSERT statement with placeholders.
            value_sets (list[tuple]): List of parameter tuples to insert.
            error_message (str): Error message for logging if insert fails.
            log_level (int): Logging level (default: logging.CRITICAL).

        Returns:
            bool: True on success, False on failure.
        """
        try:
            return self.bulk_insert_query(query, value_sets)

        except SqliteInterfaceException as ex:
            self._logger.log(log_level, "%s, reason: %s", error_message,
                             str(ex))
            self._state_object.database_health = \
                ComponentDegradationLevel.FULLY_DEGRADED
            self._state_object.database_health_state_str = "Fatal SQL failure"
            return False
