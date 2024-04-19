'''
Copyright 2014-2023 Integrated Test Management Suite

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
import logging
from quart import Blueprint, request, Response
from shared.api_view import ApiView

def create_configuration_blueprint(logger : logging.Logger):
    view = View(logger)

    blueprint = Blueprint('handshake_api', __name__)

    @blueprint.route('/configuration/add_library', methods=['POST'])
    async def add_library_request():
        return await view.add_library_handler(request)

    return blueprint

class View(ApiView):
    ''' View container class. '''

    def __init__(self, logger : logging.Logger):
        self._logger : logging.Logger = logger.getChild(__name__)

    async def add_library_handler(self, request : request):
        print("def add_library_handler(self, request : request)")

        return Response("~~PLACEHOLDEr~~", status = 500)
