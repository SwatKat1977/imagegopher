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
import logging
from quart import Blueprint, render_template, Response

def create_home_blueprint(logger : logging.Logger):
    view = View(logger)

    blueprint = Blueprint("homepage_view", __name__)

    @blueprint.route('/', methods=['GET'])
    async def home_request():
        return await view.home()

    return blueprint

class View:
    ''' Home view container class. '''

    TEMPLATE_LIBRARY_PAGE = "library.template"

    def __init__(self, logger : logging.Logger):
        self._logger = logger.getChild(__name__)

    async def home(self) -> Response:
        """
        Handler method for home page (e.g. '/').
        """

        return await render_template(self.TEMPLATE_LIBRARY_PAGE)
