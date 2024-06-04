from typing import Union, TypedDict


__all__ = ["MistConfig_Kata_Default", "MistConfig_Kata_Token", "MistConfig_Kata"]


class MistConfig_Kata_Default(TypedDict):
    theme: str
    lang: Union[str, None]
    defaulttoken: Union[int, None]


class MistConfig_Kata_Token(TypedDict):
    name: str
    instance: str
    token: str
    reacdeck: list[str]


class MistConfig_Kata(TypedDict):
    version: int
    default: MistConfig_Kata_Default
    tokens: list[MistConfig_Kata_Token]
