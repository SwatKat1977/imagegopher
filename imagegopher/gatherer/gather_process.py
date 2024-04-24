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
import os
from time import time
from typing import List
from shared.database_layer import BasePathEntry, DatabaseLayer, FileMatchState
from file_gatherer import FileGatherer
from shared.configuration.configuration import Configuration
from shared.events.event import Event

ONE_MINUTE_IN_SECONDS : int = 60

class GatherProcess:    # pylint: disable=too-few-public-methods
    ''' Class for the file gathering functionality '''
    __slots__ = ["_base_paths", "_config", "_db_layer", "_gatherers",
                 "_last_process_time", "_logger", "_refresh_config",
                 "_scan_interval"]

    def __init__(self, db_layer : DatabaseLayer,
                 logger : logging.Logger, config : Configuration) -> None:
        self._config = config
        self._db_layer = db_layer
        self._gatherers = []
        self._last_process_time : float = 0
        self._logger = logger
        self._refresh_config : bool = False

        self._scan_interval : int = \
            self._db_layer.get_config_item_scan_interval()
        self._logger.info("Scan interval time (seconds) : %d",
                          self._scan_interval)

        self._base_paths = self._cache_base_paths_from_database()
        self._base_paths.sort()

        # Generate file gatherer per base path.
        for path_entry in self._base_paths:
            gatherer = FileGatherer(self._logger, path_entry.path)
            self._gatherers.append(gatherer)

    def process_files(self):
        ''' Attempt to gather image files that are either new or modified '''
        interval : int = self._scan_interval * ONE_MINUTE_IN_SECONDS
        start_time : float = time()
        process_now : bool = False

        if self._last_process_time == 0:
            self._logger.info("First time execution of file gathering...")
            process_now = True
        elif start_time - self._last_process_time > interval:
            self._logger.info("Scheduled execution of file gathering...")
            process_now = True

        if not process_now:
            return

        for gatherer in self._gatherers:
            gathered_images = gatherer.gather_images()

            entry : BasePathEntry = [entry for entry in self._base_paths \
                                     if entry.path == gatherer.document_root]
            base_path_id : int = entry[0].row_id

            # Gathered images are grouped by directories, iterate them:
            for img in gathered_images.items():
                directory : str = img[0].removeprefix(gatherer.document_root)
                directory = directory if not directory else directory[1:]

                for file_entry in img[1]:
                    file_path : str = os.path.join(directory, file_entry[0])

                    file_hash : str = file_entry[1]
                    # Parameters : Base path id, file (with path), hash.
                    state : FileMatchState = self._db_layer.verify_file_state(
                        base_path_id, file_path, file_hash)

                    # The file matches so nothing to do...
                    if state == FileMatchState.MATCHED:
                        continue

                    if state == FileMatchState.MISSING:
                        self._logger.info(
                            "Image found '%s' (%s)",
                            os.path.join(gatherer.document_root, file_path),
                            file_hash)
                        self._db_layer.add_file_record(base_path_id,
                                                       file_path,
                                                       file_hash)
                    else:
                        self._logger.info(
                            "Image modified '%s' (%s)",
                            os.path.join(gatherer.document_root, file_path),
                            file_hash)
                        self._db_layer.update_file_record(base_path_id,
                                                          file_path,
                                                          file_hash)

        execution_time : float = time() - start_time
        self._logger.info("Execution time : %.3f (seconds)",
                          execution_time)

        # Always set last process time to current time and not to now because
        # we don't know how long processing takes.
        self._last_process_time = time()

    def db_refresh_event_handler(self, _ : Event):
        self._refresh_config = True

    def _cache_base_paths_from_database(self) -> List[BasePathEntry]:
        self._logger.info("Caching base paths from database...")
        base_paths = self._db_layer.get_base_paths()

        self._logger.info("entries base paths entries cached: %d", len(base_paths))

        return base_paths
