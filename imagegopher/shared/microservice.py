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
import asyncio
import logging

class Microservice:
    ''' Microservice framework class. '''
    __slots__ = ["_is_initialised", "_logger", "_shutdown_requested"]

    @property
    def logger(self) -> logging.Logger:
        """
        Property getter for logger instance.

        returns:
            Returns the logger instance.
        """
        return self._logger

    @logger.setter
    def logger(self, logger : logging.Logger) -> None:
        """
        Property setter for logger instance.

        parameters:
            logger (logging.Logger) : Logger instance.
        """
        self._logger = logger

    def __init__(self):
        self._is_initialised : bool = False
        self._logger : logging.Logger = None
        self._shutdown_requested : bool = False

    def initialise(self) -> bool:
        '''
        Microservice initialisation.  It should return a boolean
        (True => Successful, False => Unsuccessful), upon success
        self._is_initialised is set to True.

        returns:
            Boolean: True => Successful, False => Unsuccessful.
        '''
        if self._initialise() is True:
            self._is_initialised = True
            init_status = True

        else:
            init_status = False

        return init_status

    async def run(self) -> None:
        '''
        Start the microservice.
        '''

        while not self._shutdown_requested and self._is_initialised:
            try:
                await self._main_loop()
                await asyncio.sleep(0.1)

            except KeyboardInterrupt:
                break

        self._logger.info("Exiting microservice run loop...")

    def stop(self) -> None:
        '''
        Stop the microservice, it will wait until shutdown has been marked as
        completed before calling the shutdown method.
        '''

        self._logger.info("Stopping microservice...")
        self._logger.info('Waiting for microservice shutdown to complete')

        self._shutdown_requested = True
        self._shutdown()

        self._logger.info('Microservice shutdown complete...')

    def _initialise(self) -> bool:
        '''
        Microservice initialisation.  It should return a boolean
        (True => Successful, False => Unsuccessful).

        returns:
            Boolean: True => Successful, False => Unsuccessful.
        '''
        return True

    async def _main_loop(self) -> None:
        ''' Abstract method for main microservice loop. '''
        raise NotImplementedError("Requires implementing")

    def _shutdown(self):
        ''' Abstract method for microservice shutdown. '''
