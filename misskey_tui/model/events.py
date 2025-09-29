from typing import Callable
from threading import RLock

from misskey_tui.enum.events import UserChangeEvent


class UserChangeEventHandler:
    __handlers: list[Callable[[UserChangeEvent], None]] = []
    __lock = RLock()

    @classmethod
    def add_handler(cls, handler: Callable[[UserChangeEvent], None]) -> None:
        if not callable(handler):
            raise TypeError("handler is not function.")
        else:
            with cls.__lock:
                if handler not in cls.__handlers:
                    cls.__handlers.append(handler)

    @classmethod
    def remove_handler(cls, handler: Callable[[UserChangeEvent], None]) -> None:
        with cls.__lock:
            if handler in cls.__handlers:
                cls.__handlers.remove(handler)

    @classmethod
    def fire_event(cls, message: UserChangeEvent) -> None:
        with cls.__lock:
            # ハンドラの実行中に変更されないようにコピーを取る
            handlers = tuple(cls.__handlers)

        for handler in handlers:
            try:
                handler(message)
            except Exception:
                # 例外はとりあえず握りつぶす
                pass
