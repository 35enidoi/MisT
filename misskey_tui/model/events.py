from typing import Callable
from threading import RLock

from misskey_tui.enum.events import UserChangeEvent


class EventHandler:
    __user_change_handlers: list[Callable[[UserChangeEvent], None]] = []
    __lock = RLock()

    @classmethod
    def add_user_change_handler(cls, handler: Callable[[UserChangeEvent], None]) -> None:
        if not callable(handler):
            raise TypeError("handler is not function.")
        else:
            with cls.__lock:
                if handler not in cls.__user_change_handlers:
                    cls.__user_change_handlers.append(handler)

    @classmethod
    def fire_user_change(cls, message: UserChangeEvent) -> None:
        with cls.__lock:
            # ハンドラの実行中に変更されないようにコピーを取る
            handlers = tuple(cls.__user_change_handlers)

        for handler in handlers:
            try:
                handler(message)
            except Exception:
                # 例外はとりあえず握りつぶす
                pass

    @classmethod
    def remove_user_change_handler(cls, handler: Callable[[UserChangeEvent], None]) -> None:
        with cls.__lock:
            if handler in cls.__user_change_handlers:
                cls.__user_change_handlers.remove(handler)
