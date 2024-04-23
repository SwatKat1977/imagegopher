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
import json
import http
from types import SimpleNamespace
import typing
import jsonschema
from quart import Response
from shared.api_response import ApiResponse

class ApiView:
    """ Api view class """
    # pylint: disable=too-few-public-methods

    ERR_MSG_INVALID_BODY_TYPE : str = "Invalid body type, not JSON"
    ERR_MSG_MISSING_INVALID_JSON_BODY : str = "Missing/invalid json body"
    ERR_MSG_BODY_SCHEMA_MISMATCH : str = "Message body failed schema validation"

    CONTENT_TYPE_JSON : str = 'application/json'
    CONTENT_TYPE_TEXT : str = 'text/plain'

    def _validate_json_body(self, data : str, json_schema : dict = None) \
        -> typing.Optional[ApiResponse]:
        """
        Validate response body is JSON.

        NOTE: This has not been optimised, it can and should be in the future!

        parameters:
            data : Response body to validate.
            json_schema : Optional Json schema to validate the body against.

        returns:
            ApiResponse : If successful then object is a valid object.
        """

        if data is None:
            return ApiResponse(exception_msg=self.ERR_MSG_MISSING_INVALID_JSON_BODY,
                               status_code=http.HTTPStatus.BAD_REQUEST,
                               content_type=self.CONTENT_TYPE_TEXT)

        try:
            json_data = json.loads(data)

        except (TypeError, json.JSONDecodeError):
            return ApiResponse(exception_msg=self.ERR_MSG_INVALID_BODY_TYPE,
                               status_code=http.HTTPStatus.BAD_REQUEST,
                               content_type=self.CONTENT_TYPE_TEXT)

        # If there is a JSON schema then validate that the json body conforms
        # to the expected schema. If the body isn't valid then a 400 error
        # should be generated.
        if json_schema:
            try:
                jsonschema.validate(instance=json_data,
                                    schema=json_schema)

            except jsonschema.exceptions.ValidationError:
                return ApiResponse(exception_msg=self.ERR_MSG_BODY_SCHEMA_MISMATCH,
                                   status_code=http.HTTPStatus.BAD_REQUEST,
                                   content_type=self.CONTENT_TYPE_TEXT)

        return ApiResponse(body=json.loads(
            data, object_hook=lambda d: SimpleNamespace(**d)),
                           status_code=http.HTTPStatus.OK,
                           content_type=self.CONTENT_TYPE_JSON)

    def _generate_error_response(self, message : str):

        err_response : dict = {
            "status" : "failed",
            "message" : message
        }

        return Response(json.dumps(err_response), status=http.HTTPStatus.OK,
                        content_type=self.CONTENT_TYPE_JSON)
