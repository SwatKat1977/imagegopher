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
from http import HTTPStatus
import logging
import os
import time
import sqlite3
import quart

from burrow_configuration import BurrowConfiguration
from configuration_layout import CONFIGURATION_LAYOUT
from views.configuration_view import create_configuration_blueprint
from shared.http_helpers import ApiResponse, api_get
from shared.microservice import Microservice
from shared.version import VERSION_MAJOR, VERSION_MINOR, VERSION_BUGFIX, \
                           VERSION_POST

GATHERER_HEALTH_API_CALL : str = "{0}:{1}/health/status"

class Service(Microservice):
    """ Image Gopher Burrow microservice """
    __slots__ = ["_db_connection", "_quart"]

    def __init__(self, quart_instance) -> None:
        super().__init__()
        self._quart : quart.Quart = quart_instance
        self._db_connection = None

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

        self._logger.info("Image Gopher Burrow Microservice V%s",
                          version_str)
        self._logger.info("Copyright 2024 Image Gopher Development Team")

        if not self._manage_configuration():
            return False

        if not self._connect_to_database():
            return False

        if BurrowConfiguration().gatherer_wait_for_ok:
            self._logger.info("Waiting for gatherer to wake up...")

            if not self._check_gatherer_status():
                self._logger.fatal("Cannot get gatherer status in timely manner")
                return False
        else:
            self._logger.info("Not waiting for gatherer to wake up...")
            return True

        self._logger.info("Gatherer has reported it's awake")

        self._logger.info("Registering configuration endpoints")
        configuration_blueprint = create_configuration_blueprint(
            self._logger)
        self._quart.register_blueprint(configuration_blueprint)

        return True

    async def _main_loop(self) -> None:
        ''' Main microservice loop. '''

    def _manage_configuration(self) -> bool:
        config_file = os.getenv("GOPHER_BURROW_CONFIG", None)
        config_file_required : bool = os.getenv(
            "GOPHER_BURROW_CONFIG_REQUIRED", None)
        config_file_required = False if not config_file_required \
                               else config_file_required

        if not config_file and config_file_required:
            print("[FATAL ERROR] Configuration file missing!")
            return False

        BurrowConfiguration().configure(CONFIGURATION_LAYOUT,
                                        config_file,
                                        config_file_required)

        try:
            BurrowConfiguration().process_config()

        except ValueError as ex:
            self._logger.critical("Configuration error : %s", ex)
            return False

        self._logger.setLevel(BurrowConfiguration().logging_log_level)

        if BurrowConfiguration().gatherer_wait_for_ok_retries <= 0:
            self._logger.error(
                "Gatherer health check retries of 0 or below is invalid")
            return False

        self._logger.info("Configuration")
        self._logger.info("=============")
        self._logger.info("[logging]")
        self._logger.info("=> Logging log level          : %s",
                          BurrowConfiguration().logging_log_level)
        self._logger.info("[database]")
        self._logger.info("=> Database filename          : %s",
                          BurrowConfiguration().database_filename)
        self._logger.info("[gatherer]")
        self._logger.info("=> Gatherer                   : %s:%d",
                          BurrowConfiguration().gatherer_host,
                          BurrowConfiguration().gatherer_port)
        self._logger.info("=> Wait until running         : %s",
                          BurrowConfiguration().gatherer_wait_for_ok)
        self._logger.info("=> Wait until running retries : %s",
                          BurrowConfiguration().gatherer_wait_for_ok_retries)

        return True

    def _check_gatherer_status(self) -> bool:
        api_call : str = GATHERER_HEALTH_API_CALL.format(
            BurrowConfiguration().gatherer_host,
            BurrowConfiguration().gatherer_port)
        max_retries : int = BurrowConfiguration().gatherer_wait_for_ok_retries
        current_retries : int = 0
        now : float = time.time()
        next_retry : float = 0.0

        try:
            last_exception_msg : str = ""

            while current_retries < max_retries:
                now = time.time()
                if now >= next_retry:
                    response : ApiResponse = api_get(api_call)

                    if response.exception_msg:
                        if last_exception_msg != response.exception_msg:
                            self._logger.error(
                            "Unable to get gatherer status, reason: %s",
                            response.exception_msg)
                            last_exception_msg = response.exception_msg

                    elif response.status_code != HTTPStatus.OK:
                        msg : str = (f"Gatherer returned status : "
                                    f"{response.status_code}")

                        if last_exception_msg != response.exception_msg:
                            self._logger.error(msg)
                            last_exception_msg = response.exception_msg

                    else:
                        return True

                    next_retry = now + 10
                    current_retries += 1

                time.sleep(0.1)

        except KeyboardInterrupt:
            return False

        return False

    def _connect_to_database(self) -> bool:
        db_filename : str = BurrowConfiguration().database_filename

        if not os.path.isfile(db_filename):
            self._logger.error("Database file does NOT exist!")
            return False

        try:
            self._db_connection = sqlite3.connect(db_filename)

        except sqlite3.OperationalError as ex:
            self._logger.error("Database connect failed, reason: %s", ex)
            return False

        self._logger.info("Database connected...")

        return True
