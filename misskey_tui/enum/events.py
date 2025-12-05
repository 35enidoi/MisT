from typing import TypedDict


class UserChangeEventMessageUserChange(TypedDict):
    mistconfig_position: int
    user_name: str
    reacdeck: list[str]
    instance: str


class UserChangeEventMessageUserNone(TypedDict):
    mistconfig_position: None
    user_name: None
    reacdeck: None
    instance: None


UserChangeEvent = UserChangeEventMessageUserChange | UserChangeEventMessageUserNone


class ConfigUserAddEventMessage(TypedDict):
    name: str
    instance: str
    token: str
    reacdeck: list[str]


class ConfigUserDelEventMessage(TypedDict):
    mistconfig_position: int


ConfigUserEvent = ConfigUserAddEventMessage | ConfigUserDelEventMessage
