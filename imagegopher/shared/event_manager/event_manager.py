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
import importlib
import inspect
from collections import deque
import pkgutil
import types
from typing import Callable, Deque, Dict
from shared.event_manager.event import Event


def eventhandler(event_id: int):
    """
    Decorator to mark a function as an event handler for a specific event ID.

    Args:
        event_id (int): The unique identifier for the event type that the
                        function handles.

    Returns:
        Callable: The decorated function with an 'event_id' attribute set.
    """
    def decorator(func):
        func.event_id = event_id
        return func

    return decorator


class EventManager:
    """
    Manages registration, queuing, and processing of events.

    Attributes:
        _event_handlers (Dict[int, Callable[[Event], None]]): Mapping of event
                             IDs to their handler functions.
        _events (Deque[Event]): Queue of pending events to be processed.
        _lock (asyncio.Lock): Async lock to ensure thread-safe event queue
                              manipulation.
    """
    __slots__ = ["_event_handlers", "_events", "_lock"]

    _instance = None  # Singleton instance
    _instance_lock = asyncio.Lock()

    def __init__(self) -> None:
        """
        Initialize a new EventManager instance.
        """
        self._event_handlers: Dict[int, Callable[[Event], None]] = {}
        self._events: Deque[Event] = deque()
        self._lock = asyncio.Lock()

    @classmethod
    async def get_instance(cls) -> "EventManager":
        """
        Async-safe singleton accessor.
        Ensures only one instance is created even under concurrent calls.
        """
        async with cls._instance_lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    async def queue_event(self, event: Event) -> bool:
        """
        Queue an event for later processing if it has a registered handler.

        Args:
            event (Event): The event instance to queue.

        Returns:
            bool: True if the event was successfully queued; False if no
                  handler is registered.
        """

        if event.event_id not in self._event_handlers:
            # Invalid event id
            return False

        async with self._lock:
            self._events.append(event)

        return True

    def auto_register_handlers(self, base_module: types.ModuleType) -> None:
        """
        Automatically scan a base module and register all functions decorated
        with @handle_event.

        Args:
            base_module (types.ModuleType): The base Python module to scan for
                                            event handler functions.

        Raises:
            RuntimeError: If duplicate event IDs are detected during
                          registration.
        """
        for _, module_name, _ in pkgutil.iter_modules(base_module.__path__):
            full_module_name = f"{base_module.__name__}.{module_name}"
            module = importlib.import_module(full_module_name)

            # Top-level functions
            for _, obj in inspect.getmembers(module, inspect.isfunction):
                event_id = getattr(obj, "event_id", None)
                if event_id is not None:
                    if event_id in self._event_handlers:
                        raise RuntimeError(f"Duplicate event id {event_id}")
                    self.register_event(event_id, obj)

            # Class methods
            for _, cls in inspect.getmembers(module, inspect.isclass):
                for _, method in inspect.getmembers(cls, inspect.isfunction):
                    event_id = getattr(method, "event_id", None)
                    if event_id is not None:
                        if event_id in self._event_handlers:
                            raise RuntimeError(f"Duplicate event id {event_id}")
                        self.register_event(event_id, method)

    def register_event(self, event_id: int, callback: Callable) -> None:
        """
        Register a handler function for a specific event ID.

        Args:
            event_id (int): The unique event identifier.
            callback (Callable): The function to call when the event occurs.

        Raises:
            RuntimeError: If the event ID is already registered.
        """
        if event_id in self._event_handlers:
            raise RuntimeError(f"Duplicate event id ({event_id})")

        self._event_handlers[event_id] = callback

    async def process_next_event(self) -> None:
        """
        Process the next event in the queue by invoking its registered handler.

        If the handler is a coroutine function, it is awaited.

        Does nothing if the event queue is empty or if no handler is registered
        for the event.
        """

        async with self._lock:
            if not self._events:
                return

            event = self._events.popleft()

        handler = self._event_handlers.get(event.event_id)
        if not handler:
            # Optionally log unknown event
            return

        if inspect.iscoroutinefunction(handler):
            await handler(event)
        else:
            handler(event)

    async def delete_all_events(self) -> None:
        """
        Clear all events currently queued for processing.
        """
        async with self._lock:
            self._events.clear()

    async def process_all_events(self) -> None:
        """
        Process all events currently in the queue until it is empty.

        Events added during processing will also be processed.
        """
        while True:
            async with self._lock:
                if not self._events:
                    break
            await self.process_next_event()
