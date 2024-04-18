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
