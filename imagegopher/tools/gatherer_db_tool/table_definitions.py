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

sql_create_base_path_table : str = """
        CREATE TABLE IF NOT EXISTS base_path (
            path TEXT NOT NULL
        ); """

sql_create_file_hash_table : str = """
        CREATE TABLE IF NOT EXISTS file_hash (
            base_path_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            hash TEXT NOT NULL
        ); """

'''
Type : BOOLEAN      = 0
       FLOAT        = 1
       INT          = 2
       STRING       = 3
       UNSIGNED_INT = 4
'''
sql_create_config_item_table : str = """
        CREATE TABLE config_item (
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            type INTEGER NOT NULL CHECK (type >= 0 AND type <= 4)
        ); """
