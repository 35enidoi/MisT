from typing import Union
from dataclasses import dataclass


__all__ = ["MistConfigDefault", "MistConfigToken", "MistConfig"]


@dataclass
class MistConfigDefault:
    theme: str
    lang: Union[str, None]
    defaulttoken: Union[int, None]


@dataclass
class MistConfigToken:
    name: str | None
    instance: str
    token: str
    reacdeck: list[str]


@dataclass
class MistConfig:
    version: float
    default: MistConfigDefault
    tokens: list[MistConfigToken]
