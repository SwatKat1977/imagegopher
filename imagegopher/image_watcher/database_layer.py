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
from service_health_enums import ComponentDegradationLevel
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

    def add_base_path(self, base_path: str) -> typing.Optional[bool]:
        """ Add new base path to the database """

        query: str = "INSERT INTO base_path(path) VALUES(?)"

        exists = self.base_path_exists(base_path)

        if exists is None:
            return None

        if not exists:
            raise ValueError("Base path already exists!")

        row_id: typing.Optional[int] = self._safe_insert_query(
            query,
            (base_path,),
            error_message="Unable to add new base path",
            log_level=logging.CRITICAL
        )

        if row_id is None:
            return None

        # self._update_config_item_library_hash()

        return True

    def base_path_exists(self, base_path: str) -> typing.Optional[bool]:
        """ Check if base path exists already """

        query: str = "SELECT id FROM base_path WHERE PATH = ?"

        row = self._safe_query(query,
                               (base_path,),
                               "Unable to check if base path exists",
                               log_level=logging.CRITICAL,
                               fetch_one=True)

        if row is None:
            return False

        return bool(row)

    def _safe_query(self,
                    query: str,
                    values: tuple,
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
