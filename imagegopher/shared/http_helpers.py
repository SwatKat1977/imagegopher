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
from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import aiohttp
import requests

@dataclass(init=True)
class ApiResponse:
    """ Class for keeping track of api return data. """
    status_code: int
    body: dict | str
    content_type : str
    exception_msg : str

    def __init__(self,
                 status_code: int = 0,
                 body: dict | str = None,
                 content_type : str = None,
                 exception_msg : str = None):
        self.status_code = status_code
        self.body = body
        self.content_type = content_type
        self.exception_msg = exception_msg

CONTENT_TYPE_JSON : str = 'application/json'
CONTENT_TYPE_TEXT : str = 'text/plain'

async def async_api_post(url : str, json_data : dict = None) -> ApiResponse:
    """
    Make an API call using the POST method.

    parameters:
        url - URL of the endpoint
        json_data - Optional Json body.

    returns:
        ApiResponse which will will contain response data or just
        exception_msg if something went wrong.
    """

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=json_data) as resp:
                body = await resp.json() \
                    if resp.content_type == CONTENT_TYPE_JSON \
                    else await resp.text()
                api_return = ApiResponse(
                    status_code = resp.status,
                    body = body,
                    content_type = resp.content_type)

    except Exception as ex:
        api_return = ApiResponse(exception_msg = ex)

    return api_return

async def async_api_get(url : str, json_data : dict = None) -> ApiResponse:
    """
    Make an API call using the GET method.

    parameters:
        url - URL of the endpoint
        json_data - Optional Json body.

    returns:
        ApiResponse which will will contain response data or just
        exception_msg if something went wrong.
    """

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, json=json_data) as resp:
                body = resp.json() \
                    if resp.content_type == CONTENT_TYPE_JSON \
                    else resp.text()
                api_return = ApiResponse(
                    status_code = resp.status,
                    body = body,
                    content_type = resp.content_type)

    except Exception as ex:
        api_return = ApiResponse(exception_msg = ex)

    return api_return

def api_get(url : str, get_auth : Optional[Tuple] = None,
            get_headers : Optional[Dict] = None) -> ApiResponse:
    """
    Make an API call using the GET method.

    parameters:
    url (str) : URL of the endpoint
    get_auth (tuple) : Optional tuple to enable a certain HTTP authentication
    get_headers (dict) : Optional dictionary of HTTP headers

    returns:
    ApiResponse which will will contain response data or just exception_msg if
    something went wrong.
    """

    try:
        response : requests.Response = requests.get(url, auth=get_auth,
                                                    headers=get_headers)
        
        if response.headers["content-type"] == 'application/json; charset=utf8':
            body = response.json
        else:
            body = response.text
        content_type : str = response.headers["content-type"]

        api_response : ApiResponse = ApiResponse(
            status_code = response.status_code,
            body = body, content_type = content_type)

    except requests.exceptions.ConnectionError as ex:
        api_response : ApiResponse = ApiResponse(
            exception_msg = "Network problem (DNS failure, refused connection, etc)")

    return api_response

    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, json=json_data) as resp:
                body = resp.json() \
                    if resp.content_type == CONTENT_TYPE_JSON \
                    else resp.text()
                api_return = ApiResponse(
                    status_code = resp.status,
                    body = body,
                    content_type = resp.content_type)

    except Exception as ex:
        api_return = ApiResponse(exception_msg = ex)

    return api_return
    """
