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
import os
import typing
import quart
from configuration_layout import CONFIGURATION_LAYOUT
from gather_process import GatherProcess
from shared.configuration.configuration import Configuration
from shared.microservice import Microservice
from shared.version import VERSION_MAJOR, VERSION_MINOR, VERSION_BUGFIX, \
                           VERSION_POST


class Service(Microservice):
    """ Gopher Service microservice """

    def __init__(self, quart_instance: quart.Quart) -> None:
        super().__init__()
        self._quart: quart.Quart = quart_instance

        self._config: typing.Optional[Configuration] = None
        self._gather_process: typing.Optional[GatherProcess] = None

        # Setup logging
        self.logger = logging.getLogger(__name__)
        log_format = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            "%Y-%m-%d %H:%M:%S")
        console_stream = logging.StreamHandler()
        console_stream.setFormatter(log_format)
        self._logger.addHandler(console_stream)
        self._logger.setLevel("INFO")

    def _initialise(self) -> bool:
        """
        Method for the application initialisation.  It should return a boolean
       (True => Successful, False => Unsuccessful).

        returns:
            Boolean: True => Successful, False => Unsuccessful.
        """

        version_post: str = "" if VERSION_POST == "" \
                            else f"-{VERSION_POST}"
        version_str: str = (f"{VERSION_MAJOR}."
                            f"{VERSION_MINOR}."
                            f"{VERSION_BUGFIX}"
                            f"{version_post}")

        self._logger.info("Image Gopher: Image Watcher Microservice V%s",
                          version_str)
        self._logger.info("Copyright 2025 Image Gopher Development Team")

        config_file = os.getenv("IMAGE_GOPHER_WATCHER_CONFIG", None)
        config_file_required: bool = os.getenv(
            "IMAGE_GOPHER_WATCHER_CONFIG_REQUIRED",
            "false").lower() == "true"
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

        self._gather_process = GatherProcess(self._logger, self._config)

        return True

    async def _main_loop(self) -> None:
        """ Main microservice loop. """

    async def _shutdown(self):
        """ Shutdown logic. """

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
