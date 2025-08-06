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
from enum import Enum


class ServiceDegradationStatus(Enum):
    """ Service degradation Status """

    # Everything is working fine
    HEALTHY = 0

    # Some components are slow or experiencing minor issues
    DEGRADED = 1

    # A major component is down, affecting service functionality
    CRITICAL = 2


ServiceDegradationStatusStr: dict = {
    ServiceDegradationStatus.HEALTHY: "healthy",
    ServiceDegradationStatus.DEGRADED: "degraded",
    ServiceDegradationStatus.CRITICAL: "critical"
}

STATUS_HEALTHY: str = ServiceDegradationStatusStr[
    ServiceDegradationStatus.HEALTHY]
STATUS_DEGRADED: str = ServiceDegradationStatusStr[
    ServiceDegradationStatus.DEGRADED]
STATUS_CRITICAL: str = ServiceDegradationStatusStr[
    ServiceDegradationStatus.CRITICAL]


class ComponentDegradationLevel(Enum):
    """ Component degradation Level """

    NONE = 0
    PART_DEGRADED = 1
    FULLY_DEGRADED = 2


ComponentDegradationLevelStr: dict = {
    ComponentDegradationLevel.NONE: "none",
    ComponentDegradationLevel.PART_DEGRADED: "partial",
    ComponentDegradationLevel.FULLY_DEGRADED: "fully_degraded"
}

COMPONENT_DEGRADATION_LEVEL_NONE: str = ComponentDegradationLevelStr[
    ComponentDegradationLevel.NONE]
COMPONENT_DEGRADATION_LEVEL_DEGRADED: str = ComponentDegradationLevelStr[
    ComponentDegradationLevel.PART_DEGRADED]
COMPONENT_DEGRADATION_LEVEL_FULLY_DEGRADED: str = ComponentDegradationLevelStr[
    ComponentDegradationLevel.FULLY_DEGRADED]
