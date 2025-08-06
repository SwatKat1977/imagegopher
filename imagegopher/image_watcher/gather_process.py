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
from dataclasses import dataclass, field
import logging
import time
import typing
from gather_images import ImageGatherer
from database_layer import DatabaseLayer
from state_object import StateObject, ComponentDegradationLevel
from shared.configuration.configuration import Configuration

ONE_MINUTE_IN_SECONDS: int = 60


@dataclass
class BasePathEntry:
    id: int
    path: str


@dataclass
class GatherProcessState:
    """
    Represents the state of the gather process, including timing and control flags.

    Attributes:
        last_process_time (float): Timestamp (e.g., from time.time()) of the last gather operation.
        refresh_cache (bool): Indicates whether the cache should be forcibly refreshed
                              during the next gather operation.
    """
    last_process_time: float = 0
    refresh_cache: bool = True
    base_paths: list[BasePathEntry] = field(default_factory=list)
    degraded_state: bool = False


class GatherProcess:
    """ Class for the file gathering functionality """
    __slots__ = ["_config", "_db_layer", "_gatherers", "_logger", "_state",
                 "_state_object"]

    def __init__(self,
                 logger: logging.Logger,
                 config: Configuration,
                 db_layer: DatabaseLayer,
                 state_object: StateObject) -> None:
        self._config = config
        self._db_layer = db_layer
        self._state_object = state_object
        self._gatherers: typing.List[ImageGatherer] = []
        self._logger = logger.getChild(__name__)
        self._state = GatherProcessState()

    async def process_files(self):
        """ Attempt to gather image files that are either new or modified """

        # If in fatal degraded state, stop gathering to preserve system
        if self._state.degraded_state:
            return

        interval: int = self._config.get_entry("general",
                                               "directory_scan_interval") * \
                        ONE_MINUTE_IN_SECONDS
        start_time: float = time.time()
        process_now: bool = False

        if self._state.refresh_cache:
            if not self._cache_base_paths_from_database():
                self._state.degraded_state = True
                self._logger.critical(
                    "Caching base paths failed, service is fully degraded")
                return

            self._state.refresh_cache = False

        if self._state.last_process_time == 0:
            self._logger.info("First time execution of image gathering...")
            process_now = True

        elif start_time - self._state.last_process_time > interval:
            self._logger.info("Scheduled execution of image gathering...")
            process_now = True

        if not process_now:
            return

        for gatherer in self._gatherers:
            gathered_images = await gatherer.gather()

            for entry in gathered_images.keys():
                file_dir: str = entry.removeprefix(gatherer.document_root)
                file_dir = file_dir if not file_dir else file_dir[1:]

                print(f"[DIR] {file_dir}")

                #                directory : str = img[0].removeprefix(gatherer.document_root)
                # directory = directory if not directory else directory[1:]
            #print(gathered_images)

        execution_time: float = time.time() - start_time
        self._logger.info("Execution time : %.3f (seconds)",
                          execution_time)

        # Always set last process time to current time and not to now because
        # we don't know how long processing takes.
        self._state.last_process_time = time.time()

    def _cache_base_paths_from_database(self) -> bool:
        self._logger.info("Started caching base paths...")

        base_paths = self._db_layer.get_base_paths()

        base_path_entries: list = []

        if base_paths is None:
            self._state_object.service_health = \
                ComponentDegradationLevel.FULLY_DEGRADED
            self._state_object.database_health_state_str = "Cannot cannot " \
                "base paths, gatherer fully degraded"

        for base_path_id, base_path_path in base_paths:
            # Create base path entry for each base path
            entry: BasePathEntry = BasePathEntry(base_path_id, base_path_path)
            base_path_entries.append(entry)
            self._logger.debug("Cached base path: ID: %d : '%s'",
                               base_path_id, base_path_path)

            # Create a gatherer for the base path
            gatherer: ImageGatherer = ImageGatherer(self._logger,
                                                    base_path_path)
            self._gatherers.append(gatherer)

        self._state.base_paths = sorted(base_path_entries, key=lambda x: x.path)

        self._logger.info("Successfully cached base paths...")

        return True
