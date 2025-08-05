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
import asyncio
import os
import sys
from quart import Quart
from service import Service


app = Quart(__name__)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

SERVICE_APP: Service = Service(app)


@app.before_serving
async def startup() -> None:
    """
    Code executed before Quart has started serving http requests.
    """
    if not await SERVICE_APP.initialise():
        os._exit(1)

    app.background_task = asyncio.create_task(SERVICE_APP.run())


@app.after_serving
async def shutdown() -> None:
    """
    Code executed after Quart has stopped serving http requests.
    """
    SERVICE_APP.shutdown_event.set()
    task = getattr(app, "background_task", None)
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
