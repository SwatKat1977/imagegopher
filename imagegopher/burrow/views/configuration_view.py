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
from http import HTTPStatus
import json
import logging
import mimetypes
from quart import Blueprint, request, Response
from shared.api_view import ApiView
from database_layer import DatabaseLayer

def create_configuration_blueprint(logger : logging.Logger,
                                   db_layer : DatabaseLayer):
    view = View(logger, db_layer)

    blueprint = Blueprint('handshake_api', __name__)

    logger.info("=> Added route : /configuration/add_library")
    @blueprint.route('/configuration/add_library', methods=['POST'])
    async def add_library_request():
        return await view.add_library_handler(request)

    return blueprint

class View(ApiView):
    ''' View container class. '''

    def __init__(self, logger : logging.Logger, db_layer : DatabaseLayer):
        self._db_layer = db_layer
        self._logger : logging.Logger = logger.getChild(__name__)

        mimetypes.init()

    async def add_library_handler(self, request : request):

        try:
            if not self._db_layer.add_base_path("/usr/trial"):
                response : dict = {
                    "status" : "FAIL",
                    "exception" : "Internal error"
                }
                return Response(json.dumps(response), status=HTTPStatus.OK,
                                content_type=mimetypes.types_map['.json'])

        except ValueError as ex:
            response : dict = {
                "status" : "FAIL",
                "exception" : str(ex)
            }
            return Response(json.dumps(response), status=HTTPStatus.OK,
                            content_type=mimetypes.types_map['.json'])

        response : dict = { "status" : "OK" }
        return Response(json.dumps(response), status=HTTPStatus.OK,
                        content_type=mimetypes.types_map['.json'])
