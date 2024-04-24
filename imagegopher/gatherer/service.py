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
import logging
import os
import sqlite3
from time import time
import quart
from configuration_layout import CONFIGURATION_LAYOUT
from event_type import EventType
from shared.database_layer import DatabaseLayer
from shared.events.event import Event
from gather_process import GatherProcess
from gatherer_event_handler import GathererEventHandler
from views.health_view import create_health_blueprint
from shared.configuration.configuration import Configuration
from shared.microservice import Microservice
from shared.version import VERSION_MAJOR, VERSION_MINOR, VERSION_BUGFIX, \
                           VERSION_POST

ONE_MINUTE_SECONDS : int = 60

@dataclass(init=False)
class GathererState:
    """ Class for keeping track of gatherer state. """

    # Last time the configuration was updated (from database).
    last_db_update: int = 0

    # Timestamp that the database was cheched for updates.
    last_db_update_check : int = 0

    trigger_refresh_timestamp : int = 0

class Service(Microservice):
    """ Gopher Service microservice """
    __slots__ = ["_config", "_database_layer", "_db_connection",
                 "_gather_process", "_quart", "_state"]

    def __init__(self, quart_instance) -> None:
        super().__init__()
        self._quart : quart.Quart = quart_instance
        self._config : Configuration = None
        self._database_layer : sqlite3.Connection = None
        self._db_connection : sqlite3.Connection = None
        self._gather_process : GatherProcess = None
        self._state : GathererState = GathererState()

        self._logger = logging.getLogger(__name__)
        log_format= logging.Formatter("%(asctime)s [%(levelname)s] %(message)s",
                                      "%Y-%m-%d %H:%M:%S")
        console_stream = logging.StreamHandler()
        console_stream.setFormatter(log_format)
        self._logger.addHandler(console_stream)
        self._logger.setLevel("INFO")

    def _initialise(self) -> bool:
        '''
        Method for the application initialisation.  It should return a boolean
       (True => Successful, False => Unsuccessful).

        returns:
            Boolean: True => Successful, False => Unsuccessful.
        '''

        version_post : str = "" if VERSION_POST == "" \
                             else f"-{VERSION_POST}"
        version_str : str = (f"{VERSION_MAJOR}."
                             f"{VERSION_MINOR}."
                             f"{VERSION_BUGFIX}"
                             f"{version_post}")

        self._logger.info("Image Gopher Gatherer Microservice V%s",
                          version_str)
        self._logger.info("Copyright 2024 Image Gopher Development Team")

        config_file = os.getenv("GOPHER_GATHERER_CONFIG", None)
        config_file_required : bool = os.getenv(
            "GOPHER_GATHERER_CONFIG_REQUIRED", None)
        config_file_required = False if not config_file_required \
                               else config_file_required

        if not config_file and config_file_required:
            print("[FATAL ERROR] Configuration file missing!")
            return False

        self._config = Configuration()
        self._config.configure(CONFIGURATION_LAYOUT,
                               config_file,
                               config_file_required)

        try:
            self._config.process_config()

        except ValueError as ex:
            self._logger.critical("Configuration error : %s", ex)
            return False

        self._logger.setLevel(self._config.get_entry("logging", "log_level"))

        self._display_configuration_details()

        if not self._connect_to_database():
            return False

        self._gather_process = GatherProcess(self._database_layer,
                                             self._logger, self._config)

        self._register_events()

        self._logger.info("Registering health endpoints...")
        health_blueprint = create_health_blueprint()
        self._quart.register_blueprint(health_blueprint)

        return True

    async def _main_loop(self) -> None:
        ''' Main microservice loop. '''

        now : int = int(time())
        check_time : int = self._state.last_db_update_check + \
              int(self._config.get_entry("general",
                                         "config_check_interval"))

        if now >= check_time:
            timestamp : int = self._database_layer.get_config_item_last_update()
            if timestamp != self._state.last_db_update:
                self._logger.info(
                    "1 or more config items changing, scheduling refresh")
                self._state.trigger_refresh_timestamp = now + \
                    (1 * ONE_MINUTE_SECONDS)
                self._state.last_db_update = timestamp

            self._state.last_db_update_check = now

        if self._state.trigger_refresh_timestamp and \
           now >= self._state.trigger_refresh_timestamp:
            self._logger.info("Scheduled dynamic config refresh event added")

            GathererEventHandler().queue_event(
                Event(EventType.RefreshConfiguration))
            self._state.trigger_refresh_timestamp = 0

        GathererEventHandler().process_next_event()

        self._gather_process.process_files()

    def _display_configuration_details(self):
        self._logger.info("Configuration")
        self._logger.info("=============")
        self._logger.info("[logging]")
        self._logger.info("=> Logging log level               : %s",
                          self._config.get_entry("logging", "log_level"))
        self._logger.info("[database]")
        self._logger.info("=> Filename                        : %s",
                          self._config.get_entry("database", "filename"))
        self._logger.info("[general]")
        self._logger.info("=> Config Check Interval (seconds) : %s",
                          self._config.get_entry("general",
                                                 "config_check_interval"))

    def _shutdown(self):
        ''' Shutdown logic. '''

        self._logger.info("Closing database...")
        if self._db_connection:
            self._db_connection.close()

    def _connect_to_database(self) -> bool:
        db_filename : str = self._config.get_entry("database", "filename")

        if not os.path.isfile(db_filename):
            self._logger.error("Database file does NOT exist!")
            return False

        try:
            self._db_connection = sqlite3.connect(db_filename)

        except sqlite3.OperationalError as ex:
            self._logger.error("Database connect failed, reason: %s", ex)
            return False

        self._logger.info("Database connected...")

        self._database_layer = DatabaseLayer(self._logger, self._db_connection)

        self._state.last_db_update = \
            self._database_layer.get_config_item_last_update()
        if not self._state.last_db_update:
            return False

        self._state.last_db_update_check = int(time())

        return True

    def _register_events(self) -> None:
         self._logger.info("Registering 'RefreshConfiguration' event handler")
         GathererEventHandler().register_event(
             EventType.RefreshConfiguration,
             self._gather_process.db_refresh_event_handler)

