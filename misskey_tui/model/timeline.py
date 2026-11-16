from misskey_tui.enum.misskeypy_return import Note
from misskey_tui.enum import events
from misskey_tui.enum.timeline import Timeline
from misskey_tui.model.mkapi import MkAPIs
from misskey_tui.model.events import timeline_hundler


class TimelineService:
    __mkapi: MkAPIs
    __current_tl: Timeline
    __notes: list[Note]
    __index: int = 0

    def __init__(self, mkapi: MkAPIs) -> None:
        self.__mkapi = mkapi
        self.__current_tl = Timeline.HOME
        self.__notes = []
        self.__index = 0

        self.__mkapi.add_on_change_instance(self.clear)

    @property
    def current_tl(self) -> Timeline:
        return self.__current_tl

    @property
    def notes(self) -> list[Note]:
        return self.__notes

    @property
    def index(self) -> int:
        return self.__index

    @index.setter
    def index(self, i: int) -> None:
        if 0 <= i < len(self.__notes):
            self.__index = i
        else:
            raise IndexError("Index out of range")

    def refresh(self) -> bool:
        if self.__mkapi.is_valid_misskeypy is False:
            timeline_hundler.fire(events.TimelineErrorChangeEvent(
                action="error",
                reason="misskeypy_invalid",
                detail=None
            ))
            return False
        else:
            try:
                notes = self.__mkapi.mk_get_tl(self.__current_tl, limit=100)
            except ValueError as e:
                timeline_hundler.fire(events.TimelineErrorChangeEvent(
                    action="error",
                    reason=e.args[0] if e.args else "unknown",
                    detail=e
                ))
                return False

            if notes is not None:
                if self.__notes:
                    current_node_id = self.__notes[self.__index]["id"]
                    self.__notes = notes

                    for index, note in enumerate(self.__notes):
                        if note["id"] == current_node_id:
                            self.__index = index
                            break
                    else:
                        self.__index = len(self.__notes) - 1 if self.__notes else 0
                else:
                    self.__notes = notes
                    self.__index = 0

                timeline_hundler.fire(events.TimelineRefreshSuccessEvent(
                    action="refresh",
                    reason=None,
                    detail=None  # TODO: 何か入れる(入れない可能性もある)
                ))

                return True
            else:
                timeline_hundler.fire(events.TimelineErrorChangeEvent(
                    action="error",
                    reason="unknown",  # TODO: reasonの情報を増やす
                    detail=None
                ))
                return False

    def clear(self) -> None:
        self.__notes = []
        self.__index = 0

        timeline_hundler.fire(events.TimelineClearEvent(
            action="clear",
            reason=None,
            detail=None
        ))

    def set_tl(
            self,
            tl: Timeline) -> None:
        if tl not in Timeline:
            raise ValueError("Invalid timeline type")

        if tl in {Timeline.HOME, Timeline.HYBRID} and self.__mkapi.nowuser is None:
            timeline_hundler.fire(events.TimelineErrorChangeEvent(
                action="error",
                reason="token_missing",
                detail=None
            ))
            return

        self.__current_tl = tl
        self.__notes = []
        self.__index = 0

        timeline_hundler.fire(events.TimelineTLChangeEvent(
            action="tl_change",
            reason=None,
            detail={"tl": tl}
        ))

    @property
    def notes_count(self) -> int:
        return len(self.__notes)
