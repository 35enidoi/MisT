from typing import Callable, TypeVar, Generic
from threading import RLock

from misskey_tui.enum.events import ConfigUserEvent


T = TypeVar('T')


class _EventDispatcher(Generic[T]):
    def __init__(self):
        self.__handlers: list[Callable[[T], None]] = []
        self.__lock = RLock()

    def add_handler(self, handler: Callable[[T], None]) -> None:
        if not callable(handler):
            raise TypeError("handler is not function.")
        with self.__lock:
            if handler not in self.__handlers:
                self.__handlers.append(handler)

    def fire(self, message: T) -> None:
        with self.__lock:
            handlers = tuple(self.__handlers)

        for handler in handlers:
            try:
                handler(message)
            except Exception:
                pass

    def remove_handler(self, handler: Callable[[T], None]) -> None:
        with self.__lock:
            if handler in self.__handlers:
                self.__handlers.remove(handler)


config_user_hundler = _EventDispatcher[ConfigUserEvent]()
