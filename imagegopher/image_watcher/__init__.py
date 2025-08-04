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
import sys
from quart import Quart
#from service import Service

app = Quart(__name__)
#SERVICE_APP = None


@app.before_serving
async def startup() -> None:
    """
    Code executed before Quart has started serving http requests.
    """
    #app.add_background_task(SERVICE_APP.run)


@app.after_serving
async def shutdown() -> None:
    """
    Code executed after Quart has stopped serving http requests.
    """
    #SERVICE_APP.stop()


#SERVICE_APP = Service(app)
#if not SERVICE_APP.initialise():
#    sys.exit()
