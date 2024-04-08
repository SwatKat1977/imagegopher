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
import sqlite3

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

    def __init__(self, db : sqlite3.Connection) -> None:
        self._db_connection : sqlite3.Connection = db

    def get_base_paths(self) -> list:
        cursor = self._db_connection.cursor()

        result = cursor.execute("SELECT rowid, path FROM base_path")
        raw_results : list = result.fetchall()

        paths : list[BasePathEntry] = []
        for raw_entry in raw_results:
            entry = BasePathEntry(raw_entry[0], raw_entry[1])
            paths.append(entry)

        return paths
