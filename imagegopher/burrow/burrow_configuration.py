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
from shared.configuration.configuration import Configuration
from shared.singleton import Singleton

class BurrowConfiguration(Configuration, metaclass = Singleton):
    """ Singleton for the config """

    @property
    def logging_log_level(self) -> str:
        """ Configuration property : Logging | log level """
        return BurrowConfiguration().get_entry("logging", "log_level")

    @property
    def database_filename(self) -> str:
        """ Configuration property : Database | filename """
        return BurrowConfiguration().get_entry("database", "filename")

    @property
    def gatherer_host(self) -> str:
        """ Configuration property : Gatherer host """
        return BurrowConfiguration().get_entry("gatherer", "gatherer_host")

    @property
    def gatherer_port(self) -> int:
        """ Configuration property : Gatherer port """
        return BurrowConfiguration().get_entry("gatherer", "gatherer_port")

    @property
    def gatherer_wait_for_ok(self) -> int:
        """ Configuration property : Wait for Gatherer to be ready """
        return BurrowConfiguration().get_entry("gatherer", "wait_for_ok")

    @property
    def gatherer_wait_for_ok_retries(self) -> int:
        """ Configuration property : Wait for Gatherer to be ready retries """
        return BurrowConfiguration().get_entry("gatherer",
                                               "wait_for_ok_retries")
