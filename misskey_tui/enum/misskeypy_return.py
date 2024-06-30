from __future__ import annotations
from typing import TypedDict, Union, Literal


__all__ = [
    "BadgeRole", "Instance", "AvatarDecoration",
    "User", "FilePropertie", "Folder",
    "File", "PollChoices", "Poll",
    "Channel", "Note"
]


class BadgeRole(TypedDict):
    name: str
    iconUrl: Union[str, None]
    displayOrder: int
    behavior: str


class Instance(TypedDict):
    name: Union[str, None]
    softwareName: Union[str, None]
    softwareVersion: Union[str, None]
    iconUrl: Union[str, None]
    faviconUrl: Union[str, None]
    themeColor: Union[str, None]


class AvatarDecoration(TypedDict):
    id: str
    angle: int
    flipH: bool
    url: str
    offsetX: int
    offsetY: int


class User(TypedDict):
    id: str
    name: Union[str, None]
    username: str
    host: Union[str, None]
    avatarUrl: Union[str, None]
    avatarBlurhash: Union[str, None]
    avatarDecorations: list[AvatarDecoration]
    isBot: bool
    isCat: bool
    instance: Instance
    emojis: dict[str, int]
    onlineStatus: Literal["unknown", "online", "active", "offline"]
    badgeRoles: list[BadgeRole]


class FilePropertie(TypedDict):
    width: int
    height: int
    orientation: int
    avgColor: str


class Folder(TypedDict):
    id: str
    createdAt: Literal["YYYY-MM-DDTHH:MM:SSZ"]
    name: str
    parentId: Union[str, None]
    foldersCount: int
    filesCount: int
    parent: Folder


class File(TypedDict):
    id: str
    createdAt: Literal["YYYY-MM-DDTHH:MM:SSZ"]
    name: str
    type: str
    md5: str
    size: int
    isSensitive: bool
    blurhash: Union[str, None]
    properties: FilePropertie
    url: str
    thumbnailUrl: Union[str, None]
    comment: Union[str, None]
    folderId: Union[str, None]
    folder: Folder
    userId: Union[str, None]
    user: User


class PollChoices(TypedDict):
    isVoted: bool
    text: str
    votes: int


class Poll(TypedDict):
    expiresAt: Union[Literal["YYYY-MM-DDTHH:MM:SSZ"], None]
    multiple: bool
    choices: list[PollChoices]


class Channel(TypedDict):
    id: str
    name: str
    color: str
    isSensitive: bool
    allowRenoteToExternal: bool
    userId: Union[str, None]


class Note(TypedDict):
    """misskeyのノート型"""
    id: str
    createdAt: Literal["YYYY-MM-DDTHH:MM:SSZ"]
    deletedAt: Union[Literal["YYYY-MM-DDTHH:MM:SSZ"], None]
    text: Union[str, None]
    cw: Union[str, None]
    userId: str
    user: User
    replyId: Union[str, None]
    renoteId: Union[str, None]
    reply: Union[Note, None]
    renote: Union[Note, None]
    isHidden: bool
    visibility: Literal["public", "home", "followers", "specified"]
    mentions: list[str]
    visibleUserIds: list[str]
    fileIds: list[str]
    files: list[File]
    tags: list[str]
    poll: Union[Poll, None]
    emojis: dict[str, str]
    channelId: Union[str, None]
    channel: Union[Channel, None]
    localOnly: bool
    reactionAcceptance: Union[str, None]
    reactionEmojis: dict[str, str]
    reactions: dict[str, str]
    reactionCount: int
    renoteCount: int
    repliesCount: int
    uri: str
    url: str
    reactionAndUserPairCache: list[str]
    clippedCount: int
    myReaction: Union[str, None]
