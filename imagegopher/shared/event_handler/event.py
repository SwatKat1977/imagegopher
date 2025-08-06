
from typing import Any, Optional


class Event:
    """ Event class """
    __slots__ = ["_body", "_id"]

    @property
    def event_id(self):
        """ Property : Event id """
        return self._id

    @property
    def body(self) -> Any:
        """ Property : Event body """
        return self._body

    def __init__(self, event_id: int, body: Optional[Any] = None):
        self._id: int = event_id
        self._body: Optional[Any] = body
