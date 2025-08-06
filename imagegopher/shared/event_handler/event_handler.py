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
import inspect
from collections import deque
from typing import Callable, Deque, Dict
from shared.events.event import Event


class EventHandler:
    __slots__ = ["_event_handlers", "_events", "_lock"]

    def __init__(self) -> None:
        self._event_handlers: Dict[int, Callable[[Event], None]] = {}
        self._events: Deque[Event] = deque()
        self._lock = asyncio.Lock()

    async def queue_event(self, event: Event) -> bool:
        # Add event to queue.  Validate that the event is known about. If it is
        # then add it to the event queue for processing otherwise return
        # unknown status.
        if event.event_id not in self._event_handlers:
            # Invalid event id
            return False

        async with self._lock:
            self._events.append(event)

        return True

    def register_event(self, event_id: int, callback: Callable) -> None:
        if event_id in self._event_handlers:
            raise RuntimeError(f"Duplicate event id ({event_id})")

        self._event_handlers[event_id] = callback

    async def process_next_event(self) -> None:
        """Process the next event in the queue, if any."""

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
        """Clear all queued events."""
        async with self._lock:
            self._events.clear()

    async def process_all_events(self) -> None:
        """Process all events currently in the queue."""
        while True:
            async with self._lock:
                if not self._events:
                    break
            await self.process_next_event()
