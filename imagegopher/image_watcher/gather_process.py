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
from dataclasses import dataclass
import logging
import typing
from gather_images import ImageGatherer
from shared.configuration.configuration import Configuration

ONE_MINUTE_IN_SECONDS: int = 60


@dataclass
class GatherProcessState:
    last_process_time: float = 0
    refresh_cache: bool = False


class GatherProcess:
    """ Class for the file gathering functionality """
    __slots__ = ["_config", "_db_layer", "_gatherers", "_logger", "_state",]

    def __init__(self, logger: logging.Logger, config: Configuration) -> None:
        self._config = config
        self._db_layer = None   # TEMPORARY UNTIL IMPLEMENTED
        self._gatherers: typing.List[ImageGatherer] = []
        self._logger = logger.getChild(__name__)
        self._state = GatherProcessState()
