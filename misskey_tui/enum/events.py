from typing import TypedDict


class ConfigUserChangeEventMessage(TypedDict):
    mistconfig_position: int
    user_name: str
    reacdeck: list[str]
    instance: str


class ConfigUserNoneChangeEventMessage(TypedDict):
    mistconfig_position: None
    user_name: None
    reacdeck: None
    instance: None


class ConfigUserAddEventMessage(TypedDict):
    name: str
    instance: str
    token: str
    reacdeck: list[str]


class ConfigUserDelEventMessage(TypedDict):
    mistconfig_position: int


ConfigUserEvent = ConfigUserChangeEventMessage | ConfigUserNoneChangeEventMessage \
    | ConfigUserAddEventMessage | ConfigUserDelEventMessage
