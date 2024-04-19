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
import unittest
from unittest.mock import patch
from shared.configuration import configuration_setup
from shared.configuration.configuration import Configuration


empty_layout = configuration_setup.ConfigurationSetup(
    {
    }
)

class TestConfiguration(unittest.TestCase):

    def setUp(self):
        self._config = Configuration()

    def test_required_config(self):
        config_file : str = "invalid"
        required : bool = True
        self._config.configure(empty_layout, config_file, required)

        with self.assertRaises(ValueError) as ex:
            self._config.process_config()

        self.assertEqual("Failed to open required config file 'invalid'",
                         str(ex.exception))

        required : bool = False
        self._config.configure(empty_layout, config_file, required)

        try:
            self._config.process_config()

        except ValueError as ex:
            self.fail(str(ex))

    def test_int_type(self):

        invalid_default = configuration_setup.ConfigurationSetup(
            {
                "type_checking": [
                    configuration_setup.ConfigurationSetupItem(
                        "int", configuration_setup.ConfigItemDataType.INT,
                        default_value="INFO")
                ],
            }
        )

        config_file : str = "invalid"
        required : bool = False
        self._config.configure(invalid_default, config_file, required)

        with self.assertRaises(ValueError) as ex:
            self._config.process_config()

        self.assertEqual(
            "Configuration option 'int' with a value of 'INFO' is not an int.",
            str(ex.exception))

        valid_default = configuration_setup.ConfigurationSetup(
            {
                "type_checking": [
                    configuration_setup.ConfigurationSetupItem(
                        "int", configuration_setup.ConfigItemDataType.INT,
                        default_value="1701")
                ],
            }
        )

        config_file = "unittests/shared/valid_int_type.ini"
        self._config.configure(valid_default, config_file, True)

        try:
            self._config.process_config()

        except ValueError as ex:
            self.fail(str(ex))

        # ---------------------------------------------------------------------
        # Test configparser.NoOptionError exception raised from getint()
        # ---------------------------------------------------------------------
        with patch.object(self._config._parser, "getint",
                          side_effect=configparser.NoOptionError("option",
                                                                 "section")):
            self._config.process_config()
            # No option exception means the default value is used, check...
            self.assertEqual(self._config.get_entry("type_checking", "int"),
                             1701)

        # ---------------------------------------------------------------------
        # Test configparser.NoSectionError exception raised from getint()
        # ---------------------------------------------------------------------
        with patch.object(self._config._parser, "getint",
                          side_effect=configparser.NoSectionError("section")):
            self._config.process_config()
            # No section exception means the default value is used, check...
            self.assertEqual(self._config.get_entry("type_checking", "int"),
                             1701)

        config_file = "unittests/shared/invalid_int_type.ini"
        self._config.configure(valid_default, config_file, True)

        with self.assertRaises(ValueError) as ex:
            self._config.process_config()

        self.assertEqual(
            "Config file option 'int' is not a valid int.",
            str(ex.exception))

        # ---------------------------------------------------------------------
        # Test for missing required int configuration item
        # ---------------------------------------------------------------------
        layout = configuration_setup.ConfigurationSetup(
            {
                "type_checking": [
                    configuration_setup.ConfigurationSetupItem(
                        "required_int", configuration_setup.ConfigItemDataType.INT,
                        is_required=True)
                ],
            }
        )

        config_file = "unittests/shared/empty.ini"
        self._config.configure(layout, config_file, True)
        with self.assertRaises(ValueError) as ex:
            self._config.process_config()

        self.assertEqual(
            "Missing required config option 'type_checking::required_int'",
            str(ex.exception))
