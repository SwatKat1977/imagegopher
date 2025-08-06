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
import time
from dataclasses import dataclass, field
from service_health_enums import ComponentDegradationLevel


@dataclass
class StateObject:
    """
    Represents the state of a service, including its health status, database
    status, version, and startup time.

    Attributes:
        service_health (ComponentDegradationLevel): The current health status
                                                    of the service.
        service_health_state_str (str): A descriptive string representing the
                                        service health state.
        database_health (ComponentDegradationLevel): The current health status
                                                     of the database.
        database_health_state_str (str): A descriptive string representing the
                                         database health state.
        version (str): The version of the service.
        startup_time (int): The timestamp (Unix time) when the service was
                            started.
    """
    service_health: ComponentDegradationLevel = ComponentDegradationLevel.NONE
    service_health_state_str: str = ""
    database_health: ComponentDegradationLevel = ComponentDegradationLevel.NONE
    database_health_state_str: str = ""
    version: str = ""
    startup_time: int = field(default_factory=lambda: int(time.time()))
