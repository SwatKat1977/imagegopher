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
from http import HTTPStatus
from quart import Blueprint, request, Response
from shared.api_view import ApiView

def create_configuration_blueprint():
    view = View()

    blueprint = Blueprint('configuration_api', __name__)

    @blueprint.route('/configuration/notify_libraries_updated', methods=['POST'])
    async def notify_libraries_updated_request():
        return await view.notify_libraries_updated_handler()

    return blueprint

class View(ApiView):
    ''' View container class. '''

    async def notify_libraries_updated_handler(self):
        print("notify_libraries_updated_handler()")
        return Response("OK", status = HTTPStatus.OK)
