from os import path as os_path
from io import BytesIO
import datetime
import json
import requests
from requests import exceptions as Req_exceprions
import gettext
from misskey import (
    Misskey,
    MiAuth,
    exceptions as Mi_exceptions,
    enum as Mi_enum
)

# 型指定用のモジュール
from asciimatics.scene import Scene
from typing import Union, Any


class MkAPIs():
    # version
    # syoumi tekitouni ageteru noha naisyo
    version = 0.42

    class WindowHundlerError(Exception):
        pass

    def __init__(self) -> None:
        # mistconfig load
        self._mistconfig_init()
        # MisT settings
        self.__window_hundler = tuple()
        self.__window_hundler: Union[tuple[str, tuple[Any]], tuple[()]]
        self.init_translation()
        # Misskey py settings
        self._misskeypy_init()
        self.mk = None
        self.tl = "LTL"
        is_ok = self.reload()
        if not is_ok:
            self.i = None

        # # import daemons
        # import daemons
        # # daemons initalize
        # self.daemon = daemons.Ds(self, self.mistconfig)
        # self._finds = self.daemon._startds()

    def window_hundler_set(self, targetscene: str, *args: Any) -> None:
        if self.__window_hundler == ():
            self.__window_hundler = (targetscene, args)
        else:
            raise self.WindowHundlerError("Window hundler not empty")

    def window_hundler_get(self, _scn: Scene) -> tuple[Any]:
        if self.__window_hundler != ():
            if _scn.name == self.__window_hundler[0]:
                ret = self.__window_hundler[1]
                self.__window_hundler = ()
                return ret
            else:
                raise self.WindowHundlerError(
                    "Scene name `{}` is not target scene `{}`".format(
                        _scn.name,
                        self.__window_hundler[0]
                    )
                )
        else:
            raise self.WindowHundlerError("Window hundler empty")

    def mistconfig_put(self, loadmode: bool = False) -> None:
        filepath = self._getpath("./mistconfig.conf")
        if loadmode:
            with open(filepath, "r") as f:
                self.mistconfig = json.loads(f.read())
        else:
            with open(filepath, "w") as f:
                f.write(json.dumps(self.mistconfig))

    def init_translation(self) -> None:
        # 翻訳ファイルを配置するディレクトリ
        path_to_locale_dir = self._getpath("../locale")

        # もしself.langがNoneなら翻訳なしに
        if self.lang is None:
            lang = ""
        else:
            lang = self.lang

        # 翻訳用クラスの設定
        translater = gettext.translation(
            'messages',                    # domain: 辞書ファイルの名前
            localedir=path_to_locale_dir,  # 辞書ファイル配置ディレクトリ
            languages=[lang],              # 翻訳に使用する言語
            fallback=True                  # .moファイルが見つからなかった時は未翻訳の文字列を出力
        )

        # Pythonの組み込みグローバル領域に_という関数を束縛する
        translater.install()

    def _mistconfig_init(self) -> None:
        if os_path.isfile(self._getpath("./mistconfig.conf")):
            # mistconfigがあったら、まずロード
            self.mistconfig_put(True)
            if self.mistconfig["version"] < self.version:
                # バージョンが下なら、mistconfigのバージョン上げ
                self.mistconfig["version"] = self.version
                # もしdefaultがなければ作る
                # v0.43で廃止予定
                if not self.mistconfig.get("default"):
                    self.mistconfig["default"] = {"theme": "default",
                                                  "lang": None,
                                                  "defaulttoken": None}
                # 保存
                self.mistconfig_put()
            self.lang = self.mistconfig["default"].get("lang")
            self.theme = self.mistconfig["default"]["theme"]
        else:
            # mistconfig無ければ
            self.lang = None
            self.theme = "default"
            self.mistconfig = {"version": self.version,
                               "default": {"theme": self.theme,
                                           "lang": self.lang,
                                           "defaulttoken": None},
                               "tokens": []}
            # 保存
            self.mistconfig_put()

    def _misskeypy_init(self) -> None:
        __DEFAULT_INSTANCE = "misskey.io"
        if (default := self.mistconfig["default"]).get("defaulttoken") or default.get("defaulttoken") == 0:
            if len(self.mistconfig["tokens"]) != 0 and (len(self.mistconfig["tokens"]) > default["defaulttoken"]):
                # defaultがあるとき
                self.i = self.mistconfig["tokens"][default["defaulttoken"]]["token"]
                self.instance = self.mistconfig["tokens"][default["defaulttoken"]]["instance"]
            else:
                # defaultがないとき
                self.i = None
                self.instance = __DEFAULT_INSTANCE
        else:
            # defaultがないとき
            self.i = None
            self.instance = __DEFAULT_INSTANCE

    def reload(self) -> bool:
        bef_mk = self.mk
        try:
            self.mk = Misskey(self.instance, self.i)
            if self.i is not None:
                self.mk.i()
            return True
        except (Mi_exceptions.MisskeyAPIException,
                Mi_exceptions.MisskeyAuthorizeFailedException,
                Req_exceprions.ConnectionError,
                Req_exceprions.ReadTimeout,
                Req_exceprions.InvalidURL):
            self.mk = bef_mk
            return False

    def miauth_load(self) -> MiAuth:
        permissions = [Mi_enum.Permissions.WRITE_NOTES.value,
                       Mi_enum.Permissions.READ_ACCOUNT.value,
                       Mi_enum.Permissions.WRITE_ACCOUNT.value,
                       Mi_enum.Permissions.READ_REACTIONS.value,
                       Mi_enum.Permissions.WRITE_REACTIONS.value,
                       Mi_enum.Permissions.READ_MESSAGING.value,
                       Mi_enum.Permissions.WRITE_MESSAGING.value,
                       Mi_enum.Permissions.READ_NOTIFICATIONS.value,
                       Mi_enum.Permissions.WRITE_NOTIFICATIONS.value]

        return MiAuth(self.instance, name="MisT", permission=permissions)

    def miauth_check(self, mia: MiAuth) -> bool:
        try:
            self.i = mia.check()
            return True
        except (Mi_exceptions.MisskeyMiAuthFailedException,
                Req_exceprions.HTTPError):
            return False

    def get_i(self) -> Union[dict, None]:
        try:
            return self.mk.i()
        except (Mi_exceptions.MisskeyAPIException,
                Req_exceprions.ConnectionError):
            return None

    def get_note(self,
                 lim: int = 100,
                 untilid=None,
                 sinceid=None) -> Union[list[dict], None]:
        try:
            if self.tl == "HTL":
                notes = self.mk.notes_timeline(lim, with_files=False, until_id=untilid, since_id=sinceid)
            elif self.tl == "LTL":
                notes = self.mk.notes_local_timeline(lim, with_files=False, until_id=untilid, since_id=sinceid)
            elif self.tl == "STL":
                notes = self.mk.notes_hybrid_timeline(lim, with_files=False, until_id=untilid, since_id=sinceid)
            elif self.tl == "GTL":
                notes = self.mk.notes_global_timeline(lim, with_files=False, until_id=untilid, since_id=sinceid)
            return sorted(notes,
                          key=lambda x: datetime.fromisoformat(x["createdAt"]).timestamp(),
                          reverse=True)
        except (Mi_exceptions.MisskeyAPIException,
                Req_exceprions.ReadTimeout):
            return None

    def get_ntfy(self) -> Union[dict, None]:
        try:
            return self.mk.i_notifications(100)
        except (Mi_exceptions.MisskeyAPIException,
                Req_exceprions.ReadTimeout):
            return None

    def get_reactiondb(self) -> None:
        try:
            ret = requests.get(f'https://{self.instance}/api/emojis')
            if ret.status_code == 200:
                self.reacdb = {}
                for i in json.loads(ret.text)["emojis"]:
                    self.reacdb[i["name"]] = i["aliases"]
                    self.reacdb[i["name"]].append(i["name"])
            else:
                self.reacdb = None
        except Req_exceprions.ConnectTimeout:
            self.reacdb = None

    def noteshow(self, noteid: str) -> Union[dict, None]:
        try:
            return self.mk.notes_show(noteid)
        except (Mi_exceptions.MisskeyAPIException,
                Req_exceprions.ReadTimeout):
            return None

    def get_instance_meta(self) -> bool:
        try:
            self.meta = self.mk.meta()
            return True
        except (Mi_exceptions.MisskeyAPIException,
                Req_exceprions.ConnectTimeout):
            return False

    def get_instance_icon(self) -> Union[BytesIO, None]:
        try:
            iconurl = self.meta["iconUrl"]
            returns = requests.get(iconurl)
            if returns.status_code == 200:
                icon = BytesIO(returns.content)
                return icon
            else:
                return None
        except Req_exceprions.ConnectTimeout:
            return None

    def create_note(self, text: str) -> Union[dict, None]:
        try:
            return self.mk.notes_create(text, self.crnoteconf["CW"],
                                        renote_id=self.crnoteconf["renoteId"],
                                        reply_id=self.crnoteconf["replyId"],
                                        visibility=self.crnoteconf["visibility"]
                                        )
        except Mi_exceptions.MisskeyAPIException:
            return None

    def create_renote(self, renoteid: str) -> Union[dict, None]:
        try:
            return self.mk.notes_create(renote_id=renoteid)
        except Mi_exceptions.MisskeyAPIException:
            return None

    def create_reaction(self, noteid: str, reaction: str) -> bool:
        try:
            return self.mk.notes_reactions_create(noteid, reaction)
        except Mi_exceptions.MisskeyAPIException:
            return False

    def _getpath(self, dirname: str) -> str:
        """相対パスから絶対パスに変える奴"""
        return os_path.abspath(os_path.join(os_path.dirname(__file__),
                                            dirname))
