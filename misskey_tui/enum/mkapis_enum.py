from typing import Union
from dataclasses import dataclass


__all__ = ["MistConfig_Kata_Default", "MistConfig_Kata_Token", "MistConfig_Kata"]


@dataclass
class MistConfig_Kata_Default:
    theme: str
    lang: Union[str, None]
    defaulttoken: Union[int, None]


@dataclass
class MistConfig_Kata_Token:
    name: str | None
    instance: str
    token: str
    reacdeck: list[str]


@dataclass
class MistConfig_Kata:
    version: float
    default: MistConfig_Kata_Default
    tokens: list[MistConfig_Kata_Token]
