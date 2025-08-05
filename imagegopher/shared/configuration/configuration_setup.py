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
import enum
import typing
from dataclasses import dataclass


class ConfigItemDataType(enum.Enum):
    """ Enumeration for configuration item data type """
    BOOLEAN = enum.auto()
    FLOAT = enum.auto()
    INT = enum.auto()
    STRING = enum.auto()
    UNSIGNED_INT = enum.auto()


@dataclass(frozen=True)
class ConfigurationSetupItem:
    """ Configuration layout class """

    item_name: str
    item_type: ConfigItemDataType
    valid_values: typing.Optional[list] = None
    is_required: bool = False
    default_value: typing.Optional[object] = None


class ConfigurationSetup:
    """
    Class that defines the configuration format.

    This class holds the configuration layout by section, where each section
    contains a list of `ConfigurationSetupItem` instances describing individual
    configuration keys.
    """

    def __init__(self, setup_items: dict) -> None:
        """
        Initialize the ConfigurationSetup.

        Args:
            setup_items: A dictionary mapping section names (str) to lists of
                         ConfigurationSetupItem instances that define expected
                         config items.
        """
        self._items = setup_items

    def get_sections(self) -> list:
        """
        Get a list of sections available.

        returns:
            List of strings that represent the sections available.
        """
        return list(self._items.keys())

    def get_section(self, name: str) -> list[ConfigurationSetupItem]:
        """
        Get the list of configuration items for a given section.

        Args:
            name: The name of the section to retrieve items for.

        Returns:
            A list of ConfigurationSetupItem instances for the section.
            Returns an empty list if the section is not found.
        """
        return self._items.get(name, [])
