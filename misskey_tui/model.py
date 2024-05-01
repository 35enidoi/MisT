from os import path as os_path
import json
from requests import exceptions as Req_exceprions
import gettext
from misskey import (
    Misskey,
    MiAuth,
    exceptions as Mi_exceptions,
    enum as Mi_enum
)

# 型指定用のモジュール
from typing import Union, Callable


class MkAPIs():
    # version
    # syoumi tekitouni ageteru noha naisyo
    version = 0.42

    def __init__(self) -> None:
        # mistconfig init
        self._mistconfig_init()
        self.lang: Union[str, None]
        self.theme: str
        # translation init
        self.init_translation()
        # Misskey.py init
        i, instance = self._mistconfig_default_load()
        self.__instance: str
        self.i: Union[str, None] = None
        # variable set
        self.__on_instance_changes: list[Callable[[], None]] = []
        self.mk: Union[Misskey, None] = None
        is_ok = self.create_mk_instance(instance)
        if is_ok:
            self.token_set(i)
        else:
            self.i = None

    @property
    def instance(self) -> str:
        return self.__instance

    def _mistconfig_init(self) -> None:
        if os_path.isfile(self._getpath("../mistconfig.conf")):
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

    def _mistconfig_default_load(self) -> tuple[Union[str, None], str]:
        __DEFAULT_INSTANCE = "misskey.io"
        if (default := self.mistconfig["default"]).get("defaulttoken") or default.get("defaulttoken") == 0:
            if len(self.mistconfig["tokens"]) != 0 and (len(self.mistconfig["tokens"]) > default["defaulttoken"]):
                # defaultがあるとき
                i = self.mistconfig["tokens"][default["defaulttoken"]]["token"]
                instance = self.mistconfig["tokens"][default["defaulttoken"]]["instance"]
            else:
                # defaultがないとき
                i = None
                instance = __DEFAULT_INSTANCE
        else:
            # defaultがないとき
            i = None
            instance = __DEFAULT_INSTANCE
        return i, instance

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

    def add_on_change_instance(self, func: Callable[[], None]) -> None:
        if callable(func):
            self.__on_instance_changes.append(func)
        else:
            raise ValueError("function can`t callable.")

    def create_mk_instance(self, instance: str) -> bool:
        bef_mk = self.mk
        if self.i is not None:
            self.i = None
        self.__instance = instance
        try:
            self.mk = Misskey(instance)
            for i in self.__on_instance_changes:
                i()
            return True
        except (Mi_exceptions.MisskeyAPIException,
                Req_exceprions.ConnectionError,
                Req_exceprions.ReadTimeout,
                Req_exceprions.InvalidURL):
            self.mk = bef_mk
            return False

    def token_set(self, token: str) -> bool:
        try:
            self.mk.token = token
            self.i = token
            return True
        except (Mi_exceptions.MisskeyAPIException,
                Mi_exceptions.MisskeyAuthorizeFailedException,
                Req_exceprions.ConnectionError,
                Req_exceprions.ReadTimeout,
                Req_exceprions.InvalidURL):
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

        return MiAuth(self.__instance, name="MisT", permission=permissions)

    def miauth_check(self, mia: MiAuth) -> bool:
        try:
            self.i = mia.check()
            return True
        except (Mi_exceptions.MisskeyMiAuthFailedException,
                Req_exceprions.HTTPError):
            return False

    def mistconfig_put(self, loadmode: bool = False) -> None:
        filepath = self._getpath("../mistconfig.conf")
        if loadmode:
            with open(filepath, "r") as f:
                self.mistconfig = json.loads(f.read())
        else:
            with open(filepath, "w") as f:
                f.write(json.dumps(self.mistconfig))

    def _getpath(self, dirname: str) -> str:
        """相対パスから絶対パスに変える奴"""
        return os_path.abspath(os_path.join(os_path.dirname(__file__),
                                            dirname))
