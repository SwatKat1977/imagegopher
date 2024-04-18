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
from typing import Callable, Dict, List
from shared.events.event import Event

class EventHandler:
    __slots__ = ["_event_handlers", "_events"]

    def __init__(self) -> None:
        self._event_handlers : Dict[int, Callable] = {}
        self._events : List[Event] = []

    # Queue a new event.
    def queue_event(self, event : Event) -> bool:
        # Add event to queue.  Validate that the event is known about, if it is
        # then add it to the event queue for processing otherwise return
        # unknown status.
        if event.event_id not in self._event_handlers:
            # Invalid event id
            return False
    
        # Add the event into the queue.
        self._events.append(event)

        return True

    # Register an event with the event manager, passing in a callback function.
    def register_event(self, id : int , callback : Callable) -> None:
        if id in self._event_handlers:
            raise RuntimeError(f"Duplicate event id ({id})")

        self._event_handlers[id] = callback
 
    # Process the next event, if any exists. An error will be generated if the
    # event ID is invalid (should never happen).
    def process_next_event(self) -> None:
        # If nothing is ready for processing, return 0 (success)
        if len(self._events) == 0:
            return

        #  Get the first event from the list. 
        event = self._events[0]

        # Check to see event ID is valid, if an unknown event ID then it will
        # get quietly deleted.
        if event.event_id not in self._event_handlers:
            self._events.pop[0]
            return

        #  Call the event processing function, this is defined by the
        #  registered callback function.
        self._event_handlers[event.event_id](event)

        #  Once the event has been handled, delete it.. The event handler
        # function should deal with issues with the event and therefore
        #  deleting should be safe.
        self._events.pop(0)

    # Delete all events.
    def delete_all_events(self) -> None:
        del self._events[:] 
