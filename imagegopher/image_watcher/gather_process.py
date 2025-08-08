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
import hashlib
import logging
import os
import time
import typing
from gather_images import ImageGatherer
from database_layer import DatabaseLayer
from state_object import StateObject, ComponentDegradationLevel
from event_ids import EventId
from shared.configuration.configuration import Configuration
from shared.event_manager.event import Event
from shared.event_manager.event_manager import EventManager

ONE_MINUTE_IN_SECONDS: int = 60


@dataclass
class BasePathEntry:
    """
    Represents a base path entry with a unique identifier and its corresponding
    file system path.

    Attributes:
        id (int): The unique identifier of the base path.
        path (str): The filesystem path associated with this entry.
    """
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
    base_paths: typing.Dict[str, BasePathEntry] = field(default_factory=dict)
    degraded_state: bool = False


class GatherProcess:
    """ Class for the file gathering functionality """
    __slots__ = ["_config", "_db_layer", "_event_manager", "_gatherers",
                 "_logger", "_state", "_state_object"]

    def __init__(self,
                 logger: logging.Logger,
                 config: Configuration,
                 db_layer: DatabaseLayer,
                 state_object: StateObject,
                 event_manager: EventManager) -> None:
        # pylint: disable=too-many-arguments, too-many-positional-arguments
        self._config = config
        self._db_layer = db_layer
        self._state_object = state_object
        self._gatherers: typing.List[ImageGatherer] = []
        self._logger = logger.getChild(__name__)
        self._state = GatherProcessState()
        self._event_manager = event_manager

        self._event_manager.register_event(
            EventId.ADD_NEW_FILE_ENTRY.value,
            self._add_new_file_details)

        self._event_manager.register_event(
            EventId.UPDATE_EXISTING_FILE_ENTRY.value,
            self._update_file_details)

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
            await self._gather_images(gatherer)

        execution_time: float = time.time() - start_time
        self._logger.info("Execution time : %.3f (seconds)",
                          execution_time)

        # Always set last process time to current time and not to now because
        # we don't know how long processing takes.
        self._state.last_process_time = time.time()

    def _cache_base_paths_from_database(self) -> bool:
        self._logger.info("Started caching base paths...")

        base_paths = self._db_layer.get_base_paths()

        base_path_entries: dict = {}

        if base_paths is None:
            self._state_object.service_health = \
                ComponentDegradationLevel.FULLY_DEGRADED
            self._state_object.database_health_state_str = "Cannot cannot " \
                "base paths, gatherer fully degraded"

        for base_path_id, base_path_path in base_paths:
            # Create base path entry for each base path
            entry: BasePathEntry = BasePathEntry(base_path_id, base_path_path)
            base_path_entries[base_path_path] = entry
            self._logger.debug("Cached base path: ID: %d : '%s'",
                               base_path_id, base_path_path)

            # Create a gatherer for the base path
            gatherer: ImageGatherer = ImageGatherer(self._logger,
                                                    base_path_path)
            self._gatherers.append(gatherer)

        self._state.base_paths = dict(sorted(base_path_entries.items()))

        self._logger.info("Successfully cached base paths...")

        return True

    async def _gather_images(self, gatherer: ImageGatherer):
        gathered_images = await gatherer.gather()

        for entry in gathered_images.keys():
            # Remove the document root from the directory, if there is one
            # then remove the delimiter.
            subdir: str = entry.removeprefix(gatherer.document_root)
            subdir = subdir if not subdir else subdir[1:]

            # To improve performance, cache all file entries for the
            # subdirectory and only create a hash if:
            # 1) Entry does not exist
            # 2) Entry exists, but last modified is different
            records = self._db_layer.get_file_entries_for_directory(
                gatherer.document_root, subdir)

            for file_entry in gathered_images[entry]:
                _, filename, scan_time, modified_time = file_entry

                cache_match = next((item for item in records
                                    if item[3] == filename), None)

                full_path: str = os.path.join(gatherer.document_root,
                                              subdir,
                                              filename)

                # If there is a match with the cache, check that the last
                # modified date matches. If no match then generate a new
                # hash and update the record with new modified date and hash.
                if cache_match is not None:
                    db_id, root_id, _, db_filename, db_hash, db_modified = cache_match

                    modified_time = int(os.path.getmtime(full_path))
                    if modified_time != db_modified:
                        event_body: dict = {
                            "root": gatherer.document_root,
                            "sub_directory": subdir,
                            "filename": filename,
                            "last_modified": modified_time
                        }
                        event: Event = Event(EventId.UPDATE_EXISTING_FILE_ENTRY.value,
                                             event_body)
                        await self._event_manager.queue_event(event)

                # New record, create hash and then add the new record to
                # the database.
                else:

                    entry = self._state.base_paths.get(gatherer.document_root)

                    modified_time = int(os.path.getmtime(full_path))
                    event_body: dict = {
                        "base_path_dir": gatherer.document_root,
                        "base_path_id": entry.id,
                        "sub_directory": subdir,
                        "filename": filename,
                        "last_modified": modified_time
                    }
                    event: Event = Event(EventId.ADD_NEW_FILE_ENTRY.value,
                                         event_body)
                    await self._event_manager.queue_event(event)

    def _generate_file_hash(self, filename: str) -> str:
        """
        Generate an MD5 hash of the specified file.

        Reads the file in binary mode and computes its MD5 checksum using
        a fixed block size to efficiently handle large files.

        Args:
            filename (str): The path to the file for which to compute the hash.

        Returns:
            str: The hexadecimal MD5 hash of the file's contents.
        """
        md5_object = hashlib.md5()
        block_size = 128 * md5_object.block_size

        with open(filename, 'rb') as file_handle:
            chunk = file_handle.read(block_size)
            while chunk:
                md5_object.update(chunk)
                chunk = file_handle.read(block_size)

        return md5_object.hexdigest()

    def _add_new_file_details(self, event: Event) -> typing.Optional[int]:
        base_path_dir: str = event.body["base_path_dir"]
        base_path_id: int = event.body["base_path_id"]
        sub_dir: str = event.body["sub_directory"]
        filename: str = event.body["filename"]
        last_modified: int = int(event.body["last_modified"])

        full_path: str = os.path.join(base_path_dir, sub_dir, filename)
        file_hash = self._generate_file_hash(full_path)

        self._logger.debug("Added new file entry: '%s' with hash '%s'",
                           full_path, file_hash)

        params = (base_path_id, sub_dir, filename, file_hash, last_modified)
        return self._db_layer.add_file_entry(params)

    def _update_file_details(self, event: Event):
        """
                            event_body: dict = {
                        "root": gatherer.document_root,
                        "sub_directory": subdir,
                        "filename": filename,
                        "last_modified": modified_time
                    }
        """
        self._logger.info("update_existing file | %s %s", event.event_id, event.body)
