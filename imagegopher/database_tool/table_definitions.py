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

sql_create_base_path_table: str = """
    CREATE TABLE IF NOT EXISTS base_path (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT PRIMARY KEY
    ); """

sql_create_file_hash_table: str = """
    CREATE TABLE IF NOT EXISTS file_hash (
        base_path_id INTEGER NOT NULL,
        filename TEXT NOT NULL,
        hash TEXT NOT NULL,
        PRIMARY KEY (base_path_id, filename),
        FOREIGN KEY (base_path_id) REFERENCES base_path(rowid),
        UNIQUE (base_path_id, filename)
    ); """

sql_create_index_for_file_hash: str = """
    CREATE INDEX IF NOT EXISTS idx_file_hash_hash ON file_hash (hash);
    """
