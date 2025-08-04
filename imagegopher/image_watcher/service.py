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
import quart
from microservice import Microservice
from version import VERSION_MAJOR, VERSION_MINOR, VERSION_BUGFIX, \
                    VERSION_POST


class Service(Microservice):
    """ Gopher Service microservice """

    def __init__(self, quart_instance: quart.Quart) -> None:
        super().__init__()
        self._quart: quart.Quart = quart_instance

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

        return True

    async def _main_loop(self) -> None:
        """ Main microservice loop. """

    async def _shutdown(self):
        """ Shutdown logic. """
