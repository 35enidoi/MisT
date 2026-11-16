from typing import Literal, Any
from dataclasses import dataclass

from misskey_tui.enum.mkapis_enum import MistConfigToken
from misskey_tui.enum.timeline import Timeline


@dataclass
class ConfigThemeChangeEventMessage:
    theme: str


@dataclass
class ConfigUserChangeEventMessage:
    mistconfig_position: int
    user: MistConfigToken


@dataclass
class ConfigUserNoneChangeEventMessage:
    pass


@dataclass
class ConfigUserAddEventMessage:
    mistconfig_position: int
    user: MistConfigToken


@dataclass
class ConfigUserDelEventMessage:
    mistconfig_position: int


ConfigUserEvent = (
        ConfigThemeChangeEventMessage |
        ConfigUserChangeEventMessage |
        ConfigUserNoneChangeEventMessage |
        ConfigUserAddEventMessage |
        ConfigUserDelEventMessage
    )


@dataclass
class TimelineRefreshSuccessEvent:
    action: Literal["refresh"]
    detail: dict | None


@dataclass
class TimelineIndexChangeEvent:
    action: Literal["index_change"]
    detail: dict[Literal["index"], int]


@dataclass
class TimelineTLChangeEvent:
    action: Literal["tl_change"]
    detail: dict[Literal["tl"], Timeline]


@dataclass
class TimelineClearEvent:
    action: Literal["clear"]


@dataclass
class TimelineErrorChangeEvent:
    action: Literal["error"]
    reason: Literal[
        "misskeypy_invalid",  # misskeypy未初期化
        "token_missing",      # トークンなし
        "invalid_tl",         # 不正なTL（HTL/STLでトークンなし）
        "unknown"             # その他のエラー
    ]
    detail: Any


TimelineEvent = (
    TimelineRefreshSuccessEvent |
    TimelineIndexChangeEvent |
    TimelineTLChangeEvent |
    TimelineClearEvent |
    TimelineErrorChangeEvent
)
