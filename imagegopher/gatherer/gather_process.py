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
import logging
from typing import List
from database_layer import BasePathEntry, DatabaseLayer
from file_gatherer import FileGatherer

class GatherProcess:
    __slots__ = ["_base_paths", "_db_layer", "_gatherers", "_logger"]

    def __init__(self, db_layer : DatabaseLayer,
                 logger : logging.Logger) -> None:
        self._db_layer = db_layer
        self._gatherers = []
        self._logger = logger

        self._base_paths = self._cache_base_paths_from_database()
        self._base_paths.sort()

        # Generate file gatherer per base path.
        for path_entry in self._base_paths:
            gatherer = FileGatherer(self._logger, path_entry.path)
            self._gatherers.append(gatherer)

    def process_files(self):
        print("process_files......")

    def _cache_base_paths_from_database(self) -> List[BasePathEntry]:
        self._logger.info("Caching base paths from database...")
        base_paths = self._db_layer.get_base_paths()
        
        self._logger.info("entries base paths entries cached: %d", len(base_paths))

        return base_paths
