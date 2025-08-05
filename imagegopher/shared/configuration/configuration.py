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
import configparser
import os
from shared.configuration.configuration_setup import ConfigItemDataType, \
                                                     ConfigurationSetup, \
                                                     ConfigurationSetupItem

class Configuration():
    """
    Class that wraps the functionality of configparser to support additional
    features such as trying multiple sources for the configuration item.
    """

    def __init__(self):
        """ Constructor for the configuration class. """

        self._parser = configparser.ConfigParser()

        self._config_file : str = ''
        self._has_config_file = False
        self._config_file_required = False
        self._layout : ConfigurationSetup = None
        self._config_items = {}

    def configure(self, layout : ConfigurationSetup,
                 config_file : str = None, file_required : bool = False):
        """
        Constructor for the configuration base class, it take in a layout
        class to validate the file.

        Example of layout:
        {
            "logging": [
                ConfigurationSetupItem(
                    "log_level", ConfigItemDataType.STRING,
                    valid_values=['DEBUG', 'INFO'],
                    default_value="INFO")
            ]
        }

        parameters:
            layout : Dictionary defining the configuration file
            config_file : Config file to read (optional, default = None)
            file_required : Is the file required (optional, default = False)
            required_files : Dict of required item (optional, default = None)
        """
        self._config_file = config_file
        self._config_file_required = file_required
        self._layout = layout

    def process_config(self):
        """
        Process the configuration
        """

        files_read = []

        if self._config_file:
            try:
                files_read = self._parser.read(self._config_file)

            except configparser.ParsingError as ex:
                raise ValueError(
                    f"Failed to read required config file, reason: {ex}") from ex

            if not files_read and self._config_file_required:
                raise ValueError(
                    f"Failed to open required config file '{self._config_file}'")

            self._has_config_file = True

        self._read_configuration()

    def get_entry(self, section : str, item : str) -> object:
        """
        Get a configuration entry item value from a section.

        parameters:
            section (str) : Name of section
            item (str) : Name of configuration item to retrieve

        returns:
            Value of entry, the type depends on the items type - e.g.
            string (str) or integer (int).
        """

        if section not in self._config_items:
            raise ValueError(f"Invalid section '{section}'")

        if item not in self._config_items[section]:
            raise ValueError(f"Invalid config item {section}::{item}'")

        return self._config_items[section][item]

    def _read_configuration(self):

        sections = self._layout.get_sections()

        for section_name in sections:
            section_items = self._layout.get_section(section_name)

            for section_item in section_items:

                if section_item.item_type == ConfigItemDataType.INT:
                    item_value : int = self._read_int(section_name, section_item)

                elif section_item.item_type == ConfigItemDataType.STRING:
                    item_value : str = self._read_str(section_name,
                                                     section_item.item_name,
                                                     section_item)

                elif section_item.item_type == ConfigItemDataType.BOOLEAN:
                    item_value : bool = self._read_bool(section_name,
                                                        section_item)

                elif section_item.item_type == ConfigItemDataType.FLOAT:
                    item_value : float = self._read_float(section_name,
                                                        section_item)
                elif section_item.item_type == ConfigItemDataType.UNSIGNED_INT:
                    item_value : int = self._read_uint(section_name,
                                                        section_item)

                if section_name not in self._config_items:
                    self._config_items[section_name] = {}

                self._config_items[section_name][section_item.item_name] = item_value

    def _read_str(self, section : str, option : str,
                 fmt : ConfigurationSetupItem) -> str:
        """
        Read a configuration option of type string, firstly it will check for
        an environment variable (format is section_option), otherwise try the
        configuration file (if it exists). An ValueError exception is thrown
        it's missing and marked as is_required.

        parameters:
            section : Configuration section
            option : Configuration option to read
            default : Default value (if not a required variable)
            is_required : Is a required env variable flag (default is False)

        returns:
            A str or None if it's not a required field.
        """
        env_variable : str = f"{section}_{option}".upper()
        value = os.getenv(env_variable)

        # If no environment variable is found, check config file (if exits)
        if not value and self._has_config_file:
            try:
                value = self._parser.get(section, option)

            except configparser.NoOptionError:
                value = None

            except configparser.NoSectionError:
                value = None

        value = value if value else fmt.default_value

        if not value and fmt.is_required:
            raise ValueError("Missing required config option "
                             f"'{section}::{fmt.item_name}'")

        if fmt.valid_values and value not in fmt.valid_values:
            raise ValueError(f"Value of '{value} for {fmt.item_name} is invalid")

        return value

    def _read_int(self, section : str,
                  fmt : ConfigurationSetupItem) -> int:
        """
        Read a configuration option of type int, firstly it will check for
        an environment variable (format is section_option), otherwise try the
        configuration file (if it exists). An ValueError exception is thrown
        it's missing and marked as is_required or is not an int.

        parameters:
            section : Configuration section
            option : Configuration option to read
            default : Default value (if not a required variable)
            is_required : Is a required env variable flag (default is False)

        returns:
            An int or None if it's not a required field.
        """
        env_variable : str = f"{section}_{fmt.item_name}".upper()
        value = os.getenv(env_variable)

        # If no environment variable is found, check config file (if exits)
        if value is None and self._has_config_file:
            try:
                value = self._parser.getint(section, fmt.item_name)

            except configparser.NoOptionError:
                value = None

            except configparser.NoSectionError:
                value = None

            except ValueError as ex:
                raise ValueError(f"Config file option '{fmt.item_name}'"
                                 " is not a valid int.") from ex

        value = value if value is not None else fmt.default_value
        if value is None and fmt.is_required:
            raise ValueError("Missing required config option "
                             f"'{section}::{fmt.item_name}'")

        try:
            value = int(value)

        except ValueError as ex:
            raise ValueError((f"Configuration option '{fmt.item_name}' with"
                              f" a value of '{value}' is not an int.")) from ex

        return value

    def _read_bool(self, section: str,
                   fmt: ConfigurationSetupItem) -> bool:
        """
        Read a configuration option of type bool, firstly it will check for
        an environment variable (format is section_option), otherwise try the
        configuration file (if it exists). An ValueError exception is thrown
        it's missing and marked as is_required or is not an int.

        parameters:
            section : Configuration section
            option : Configuration option to read
            default : Default value (if not a required variable)
            is_required : Is a required env variable flag (default is False)

        returns:
            A bool or None if it's not a required field.
        """
        env_variable : str = f"{section}_{fmt.item_name}".upper()
        value = os.getenv(env_variable)

        # If no environment variable is found, check config file (if exits)
        if value is None and self._has_config_file:
            try:
                value = self._parser.getboolean(section, fmt.item_name)

            except configparser.NoOptionError:
                value = None

            except configparser.NoSectionError:
                value = None

            except ValueError as ex:
                raise ValueError((f"Config file option '{fmt.item_name}'"
                                   " is not a valid boolean.")) from ex

        value = value if value is not None else fmt.default_value

        if not value and fmt.is_required:
            raise ValueError("Missing required config option "
                             f"'{section}::{fmt.item_name}'")

        if value.lower() in ["true", "1"]:
            value : bool = True
        elif value.lower() in ["false", "0"]:
            value : bool = False
        else:
            raise ValueError((f"Configuration option '{fmt.item_name}' with "
                              f"a value of '{value}' is not an bool."))

        return value

    def _read_float(self, section: str,
                    fmt: ConfigurationSetupItem) -> float:
        """
        Read a configuration option of type float, firstly it will check for an
        environment variable (format is section_option), otherwise try the
        configuration file (if it exists). An ValueError exception is thrown
        it's missing and marked as is_required or is not an float.

        parameters:
            section : Configuration section
            option : Configuration option to read
            default : Default value (if not a required variable)
            is_required : Is a required env variable flag (default is False)

        returns:
            An float or None if it's not a required field.
        """
        env_variable : str = f"{section}_{fmt.item_name}".upper()
        value = os.getenv(env_variable)

        # If no environment variable is found, check config file (if exits)
        if value is None and self._has_config_file:
            try:
                value = self._parser.getfloat(section, fmt.item_name)

            except configparser.NoOptionError:
                value = None

            except configparser.NoSectionError:
                value = None

            except ValueError as ex:
                raise ValueError((f"Config file option '{fmt.item_name}'"
                                  " is not a valid float.")) from ex

        value = value if value is not None else fmt.default_value

        if not value and fmt.is_required:
            raise ValueError("Missing required config option "
                             f"'{section}::{fmt.item_name}'")

        try:
            value = float(value)

        except ValueError as ex:
            raise ValueError((f"Configuration option '{fmt.item_name}' with a "
                              f"value of '{value}' is not a float.")) from ex

        return value

    def _read_uint(self, section : str,
                   fmt : ConfigurationSetupItem) -> int:
        """
        Read a configuration option of type int, firstly it will check for
        an environment variable (format is section_option), otherwise try the
        configuration file (if it exists). An ValueError exception is thrown
        it's missing and marked as is_required or is not an unsigned int.

        parameters:
            section : Configuration section
            option : Configuration option to read
            default : Default value (if not a required variable)
            is_required : Is a required env variable flag (default is False)

        returns:
            An unsigned int or None if it's not a required field.
        """
        value : int = self._read_int(section, fmt)

        if value is None:
            return value

        if value < 0:
            raise ValueError((f"Configuration option '{fmt.item_name}' with a"
                              f"value of '{value}' is not an unsigned int."))

        return value
