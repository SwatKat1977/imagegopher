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
from shared.configuration import configuration_setup

CONFIGURATION_LAYOUT = configuration_setup.ConfigurationSetup(
    {
        "logging": [
            configuration_setup.ConfigurationSetupItem(
                "log_level", configuration_setup.ConfigItemDataType.STRING,
                valid_values=['DEBUG', 'INFO'], default_value="INFO")
        ],
        "database": [
            configuration_setup.ConfigurationSetupItem(
                "filename", configuration_setup.ConfigItemDataType.STRING,
                is_required=True)
        ],
        "gatherer": [
            configuration_setup.ConfigurationSetupItem(
                "gatherer_host", configuration_setup.ConfigItemDataType.STRING,
                is_required=True),
            configuration_setup.ConfigurationSetupItem(
                "gatherer_port", configuration_setup.ConfigItemDataType.INT,
                default_value="3001"),
            configuration_setup.ConfigurationSetupItem(
                "wait_for_ok", configuration_setup.ConfigItemDataType.BOOLEAN,
                default_value="True"),
            configuration_setup.ConfigurationSetupItem(
                "wait_for_ok_retries", configuration_setup.ConfigItemDataType.INT,
                default_value="12")
        ]
    }
)
