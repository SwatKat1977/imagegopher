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
import json
import logging
import mimetypes
from quart import Blueprint, request, Response
from shared.api_view import ApiView
from shared.api_response import ApiResponse
from database_layer import DatabaseLayer

''' Definition of the add base path request schema '''
SCHEMA_REQUEST_ADDBASEPATH = \
    {
        "$schema": "http://json-schema.org/draft-07/schema#",

        "type" : "object",
        "additionalProperties" : False,

        "properties":
        {
            "path":
            {
                "type" : "string"
            }
        },
        "required" : ["path"]
    }

''' Definition of the add base path request schema '''
SCHEMA_REQUEST_ADDBASEPATH = \
    {
        "$schema": "http://json-schema.org/draft-07/schema#",

        "type" : "object",
        "additionalProperties" : False,

        "properties":
        {
            "path":
            {
                "type" : "string"
            }
        },
        "required" : ["path"]
    }

''' Definition of the set scan interval request schema '''
SCHEMA_REQUEST_SETSCANINTERVAL = \
    {
        "$schema": "http://json-schema.org/draft-07/schema#",

        "type" : "object",
        "additionalProperties" : False,

        "properties":
        {
            "interval":
            {
                "type" : "integer"
            }
        },
        "required" : ["interval"]
    }

def create_configuration_blueprint(logger : logging.Logger,
                                   db_layer : DatabaseLayer):
    view = View(logger, db_layer)

    blueprint = Blueprint('handshake_api', __name__)

    logger.info("=> Added route : /configuration/add_library")
    @blueprint.route('/configuration/add_library', methods=['POST'])
    async def add_library_request():
        return await view.add_library_handler(request)

    logger.info("=> Added route : /configuration/set_scan_interval")
    @blueprint.route('/configuration/set_scan_interval', methods=['POST'])
    async def set_scan_interval_request():
        return await view.set_scan_interval_handler(request)

    return blueprint

class View(ApiView):
    ''' View container class. '''

    def __init__(self, logger : logging.Logger, db_layer : DatabaseLayer):
        self._db_layer = db_layer
        self._logger : logging.Logger = logger.getChild(__name__)

        mimetypes.init()

    async def add_library_handler(self, api_request : request):

        request_obj : ApiResponse = self._validate_json_body(
            await api_request.get_data(), SCHEMA_REQUEST_ADDBASEPATH)

        if request_obj.status_code != HTTPStatus.OK:
            return self._generate_error_response(request_obj.exception_msg)

        try:
            if not self._db_layer.add_base_path(request_obj.body.path):
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

    async def set_scan_interval_handler(self, api_request : request):

        request_obj : ApiResponse = self._validate_json_body(
            await api_request.get_data(), SCHEMA_REQUEST_SETSCANINTERVAL)

        if request_obj.status_code != HTTPStatus.OK:
            return self._generate_error_response(request_obj.exception_msg)

        if request_obj.body.interval <= 0 or request_obj.body.interval > 32767:
              return self._generate_error_response(
                  "Interval outside range of 1 -> 32767")

        self._db_layer.update_config_item_scan_interval(
            request_obj.body.interval)

        response : dict = { "status" : "OK" }
        return Response(json.dumps(response), status=HTTPStatus.OK,
                        content_type=mimetypes.types_map['.json'])
