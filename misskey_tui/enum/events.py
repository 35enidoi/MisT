from typing import Literal
from dataclasses import dataclass


@dataclass
class ConfigUserChangeEventMessage:
    mistconfig_position: int
    user_name: str
    reacdeck: list[str]
    instance: str
    token: str


@dataclass
class ConfigUserNoneChangeEventMessage:
    pass


@dataclass
class ConfigUserAddEventMessage:
    name: str
    instance: str
    token: str
    reacdeck: list[str]


@dataclass
class ConfigUserDelEventMessage:
    mistconfig_position: int


ConfigUserEvent = (
        ConfigUserChangeEventMessage |
        ConfigUserNoneChangeEventMessage |
        ConfigUserAddEventMessage |
        ConfigUserDelEventMessage
    )


@dataclass
class TimelineRefreshSuccessEvent:
    action: Literal["refresh"]
    reason: None
    detail: dict | None


@dataclass
class TimelineIndexChangeEvent:
    action: Literal["index_change"]
    reason: None
    detail: dict[Literal["index"], int]


@dataclass
class TimelineTLChangeEvent:
    action: Literal["tl_change"]
    reason: None
    detail: dict[Literal["tl"], Literal["HTL", "LTL", "STL", "GTL"]]


@dataclass
class TimelineClearEvent:
    action: Literal["clear"]
    reason: None
    detail: None


@dataclass
class TimelineErrorChangeEvent:
    action: Literal["error"]
    reason: Literal[
        "misskeypy_invalid",  # misskeypy未初期化
        "token_missing",      # トークンなし
        "invalid_tl",         # 不正なTL（HTL/STLでトークンなし）
        "unknown"             # その他のエラー
    ]
    detail: None


TimelineChangeEvent = (
    TimelineRefreshSuccessEvent |
    TimelineIndexChangeEvent |
    TimelineTLChangeEvent |
    TimelineClearEvent |
    TimelineErrorChangeEvent
)
