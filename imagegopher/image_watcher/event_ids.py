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
import enum


class EventId(enum.Enum):
    """
    Enumeration of event identifiers used by the event system.

    Attributes:
        ADD_NEW_FILE_ENTRY (int): Event triggered when a new file record
            should be created in the system.
        UPDATE_EXISTING_FILE_ENTRY (int): Event triggered when an existing
            file record should be updated with new details.
    """
    ADD_NEW_FILE_ENTRY = 0
    UPDATE_EXISTING_FILE_ENTRY = 1
