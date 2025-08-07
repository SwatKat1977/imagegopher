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
from typing import Any, Optional


class Event:
    """ Event class """
    __slots__ = ["_body", "_id"]

    @property
    def event_id(self):
        """ Property : Event id """
        return self._id

    @property
    def body(self) -> Any:
        """ Property : Event body """
        return self._body

    def __init__(self, event_id: int, body: Optional[Any] = None):
        self._id: int = event_id
        self._body: Optional[Any] = body
