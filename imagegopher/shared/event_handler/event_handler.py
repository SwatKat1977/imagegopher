from collections import deque
from typing import Callable, Deque, Dict
from shared.events.event import Event


class EventHandler:
    __slots__ = ["_event_handlers", "_events"]

    def __init__(self) -> None:
        self._event_handlers: Dict[int, Callable] = {}
        self._events: Deque[Event] = deque()

    def queue_event(self, event: Event) -> bool:
        # Add event to queue.  Validate that the event is known about, if it is
        # then add it to the event queue for processing otherwise return
        # unknown status.
        if event.event_id not in self._event_handlers:
            # Invalid event id
            return False

        self._events.append(event)

        return True

    def register_event(self, event_id: int, callback: Callable) -> None:
        if event_id in self._event_handlers:
            raise RuntimeError(f"Duplicate event id ({event_id})")

        self._event_handlers[event_id] = callback

    def process_next_event(self) -> None:
        # If nothing is ready for processing, return.
        if len(self._events) == 0:
            return

        #  Get the first event from the list.
        event = self._events[0]

        # Check to see event ID is valid, if an unknown event ID then it will
        # get quietly deleted.
        if event.event_id not in self._event_handlers:
            self._events.popleft()
            return

        #  Call the event processing function, this is defined by the
        #  registered callback function.
        self._event_handlers[event.event_id](event)

        #  Once the event has been handled, delete it.. The event handler
        # function should deal with issues with the event and therefore
        #  deleting should be safe.
        self._events.popleft()

    def delete_all_events(self) -> None:
        self._events.clear()
