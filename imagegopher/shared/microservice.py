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
from abc import ABC, abstractmethod
import asyncio
import logging


class Microservice(ABC):
    """ Microservice framework class. """
    __slots__ = ["_is_initialised", "_logger", "_shutdown_complete",
                 "_shutdown_event"]

    def __init__(self, logger: logging.Logger):
        self._is_initialised: bool = False
        self._logger: logging.Logger = logger.getChild(__name__)
        self._shutdown_event: asyncio.Event = asyncio.Event()
        self._shutdown_complete: asyncio.Event = asyncio.Event()

    @property
    def shutdown_event(self) -> asyncio.Event:
        return self._shutdown_event

    @property
    def shutdown_complete(self) -> asyncio.Event:
        return self._shutdown_complete

    def initialise(self) -> bool:
        """
        Microservice initialisation.  It should return a boolean
        (True => Successful, False => Unsuccessful), upon success
        self._is_initialised is set to True.

        Returns:
            Boolean: True => Successful, False => Unsuccessful.
        """
        if self._initialise() is True:
            self._is_initialised = True
            return True

        self.stop()

        return False

    async def run(self) -> None:
        """
        Start the microservice.
        """

        if not self._is_initialised:
            self._logger.warning("Microservice is not initialised. Exiting run loop.")
            return

        self._logger.info("Microservice starting main loop.")

        try:
            while True:
                if self.shutdown_event.is_set():
                    break

                await self._main_loop()
                await asyncio.sleep(0.1)

        except (KeyboardInterrupt, asyncio.CancelledError):
            self._logger.info("Cancellation or keyboard interrupt received.")
            self._shutdown_event.set()

        finally:
            self._logger.info("Exiting microservice run loop...")
            await self._shutdown_complete.wait()
            self._logger.info("Shutdown complete.")

    async def stop(self) -> None:
        """
        Stop the microservice, it will wait until shutdown has been marked as
        completed before calling the shutdown method.
        """

        self._logger.info("Stopping microservice...")
        self._logger.info('Waiting for microservice shutdown to complete')

        self._shutdown_event.set()

        await self._shutdown()
        self._shutdown_complete.set()

        self._logger.info('Microservice shutdown complete...')

    def _initialise(self) -> bool:
        """
        Microservice initialisation.  It should return a boolean
        (True => Successful, False => Unsuccessful).

        Returns:
            Boolean: True => Successful, False => Unsuccessful.
        """
        return True

    @abstractmethod
    async def _main_loop(self) -> None:
        """ Abstract method for main microservice loop. """
        pass

    @abstractmethod
    async def _shutdown(self):
        """ Abstract method for microservice shutdown. """
        pass
