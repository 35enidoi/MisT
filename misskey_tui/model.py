from os import path as os_path
from glob import glob
import json
import gettext
from typing import Union, Callable, Final

from requests import exceptions as Req_exceptions
from asciimatics.widgets.utilities import THEMES
from misskey import (
    Misskey,
    MiAuth,
    exceptions as Mi_exceptions,
    enum as Mi_enum
)

# version
# syoumi tekitouni ageteru noha naisyo
VERSION = 0.42


class MkAPIs():
    def __init__(self) -> None:
        # mistconfig init
        self.__mistconfig_init()
        self.__lang: str
        self.__theme: str
        self.VERSION: Final = VERSION
        # check valid languages
        self.valid_langs: Final = tuple(os_path.basename(os_path.dirname(i)) for i in
                                        glob(self._getpath("../locale/*/LC_MESSAGES")))
        # translation init
        self.translation(self.__lang)
        # Misskey.py init
        i, instance = self.__mistconfig_default_load()
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

    @property
    def lang(self) -> str:
        return self.__lang

    @property
    def theme(self) -> str:
        return self.__theme

    @theme.setter
    def theme(self, val: str) -> None:
        if val in THEMES:
            self.__theme = val
            self.mistconfig["default"]["theme"] = val
            self.mistconfig_put()
        else:
            raise ValueError(f"theme `{val}` not in THEMES.")

    def __mistconfig_init(self) -> None:
        if os_path.isfile(self._getpath("../mistconfig.conf")):
            # mistconfigがあったら、まずロード
            self.mistconfig_put(True)
            if self.mistconfig["version"] < VERSION:
                # バージョンが下なら、mistconfigのバージョン上げ
                self.mistconfig["version"] = VERSION
                # もしdefaultがなければ作る
                # v0.43で廃止予定
                if not self.mistconfig.get("default"):
                    self.mistconfig["default"] = {"theme": "default",
                                                  "lang": None,
                                                  "defaulttoken": None}
                # 保存
                self.mistconfig_put()
            self.__lang = lang if (lang := self.mistconfig["default"].get("lang")) is not None else ""
            self.__theme = self.mistconfig["default"]["theme"]
        else:
            # mistconfig無ければ
            self.__lang = ""
            self.__theme = "default"
            self.mistconfig = {"version": VERSION,
                               "default": {"theme": self.__theme,
                                           "lang": self.__lang,
                                           "defaulttoken": None},
                               "tokens": []}
            # 保存
            self.mistconfig_put()

    def __mistconfig_default_load(self) -> tuple[Union[str, None], str]:
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

    def translation(self, lang: str) -> None:
        # 翻訳ファイルを配置するディレクトリ
        path_to_locale_dir = self._getpath("../locale")

        # ちゃんと使えるか確認
        if lang not in self.valid_langs and not lang == "":
            raise ValueError(f"language `{lang}` is invalid.")

        # 保存
        self.__lang = lang
        self.mistconfig["default"]["lang"] = self.__lang
        self.mistconfig_put()

        # 翻訳用クラスの設定
        translater = gettext.translation(
            'messages',                    # domain: 辞書ファイルの名前
            localedir=path_to_locale_dir,  # 辞書ファイル配置ディレクトリ
            languages=[self.__lang],              # 翻訳に使用する言語
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
                Req_exceptions.ConnectionError,
                Req_exceptions.ReadTimeout,
                Req_exceptions.InvalidURL):
            self.mk = bef_mk
            return False

    def token_set(self, token: str) -> bool:
        try:
            self.mk.token = token
            self.i = token
            return True
        except (Mi_exceptions.MisskeyAPIException,
                Mi_exceptions.MisskeyAuthorizeFailedException,
                Req_exceptions.ConnectionError,
                Req_exceptions.ReadTimeout,
                Req_exceptions.InvalidURL):
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
                Req_exceptions.HTTPError):
            return False

    def mistconfig_put(self, loadmode: bool = False) -> None:
        filepath = self._getpath("../mistconfig.conf")
        if loadmode:
            with open(filepath, "r") as f:
                self.mistconfig = json.loads(f.read())
        else:
            with open(filepath, "w") as f:
                f.write(json.dumps(self.mistconfig))

    @staticmethod
    def _getpath(dirname: str) -> str:
        """相対パスから絶対パスに変える奴"""
        return os_path.abspath(os_path.join(os_path.dirname(__file__),
                                            dirname))
