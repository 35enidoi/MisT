from copy import deepcopy
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

from misskey_tui.enum import (
    MisskeyPyExceptions,
    MistConfig_Kata_Token,
    MistConfig_Kata_Default,
    MistConfig_Kata
)

# version
# syoumi tekitouni ageteru noha naisyo
VERSION = 0.42


class MkAPIs():
    def __init__(self) -> None:
        self.VERSION: Final = VERSION
        # mistconfig init
        self.__mistconfig_init()
        self.mistconfig: MistConfig_Kata
        self.__lang: str
        self.__theme: str
        # check valid languages
        self.valid_langs: Final = tuple(os_path.basename(os_path.dirname(i)) for i in
                                        glob(self._getpath("../locale/*/LC_MESSAGES")))
        # translation
        self.translation(self.__lang)
        # variable set
        self.__on_instance_changes: list[Callable[[], None]] = []
        self.mk: Union[Misskey, None] = None
        self.__instance: str
        self.nowuser: Union[int, None] = None
        if self.mistconfig["default"]["defaulttoken"] is not None:
            self.select_user(self.mistconfig["default"]["defaulttoken"])
        else:
            self.connect_mk_instance("misskey.io")

    @property
    def now_user_info(self) -> Union[MistConfig_Kata_Token, None]:
        if self.nowuser is not None:
            return self.mistconfig["tokens"][self.nowuser].copy()
        else:
            return None

    @property
    def users_info(self) -> list[MistConfig_Kata_Token]:
        return deepcopy(self.mistconfig["tokens"])

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
            self.mistconfig = MistConfig_Kata(version=self.VERSION,
                                              default=MistConfig_Kata_Default(theme=self.__theme,
                                                                              lang=self.__lang,
                                                                              defaulttoken=None),
                                              tokens=[])
            # 保存
            self.mistconfig_put()

    def translation(self, lang: str) -> None:
        # 翻訳ファイルを配置するディレクトリ
        path_to_locale_dir = self._getpath("../locale")

        # ちゃんと使えるか確認
        if lang not in self.valid_langs and lang != "":
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

    def connect_mk_instance(self, instance: str) -> bool:
        bef_mk = self.mk
        self.__instance = instance
        try:
            self.mk = Misskey(instance)
            self.nowuser = None
            for i in self.__on_instance_changes:
                i()
            return True
        except (MisskeyPyExceptions,
                Req_exceptions.InvalidURL):
            self.mk = bef_mk
            return False

    def add_user(self, token: str) -> bool:
        try:
            self.mk.token = token
            try:
                name = self.mk.i()["name"]
            except MisskeyPyExceptions:
                name = "Fail to get user info"
            self.mistconfig["tokens"].append(MistConfig_Kata_Token(name=name,
                                                                   instance=self.__instance,
                                                                   token=token,
                                                                   reacdeck=[]))
            return True
        except (MisskeyPyExceptions,
                Mi_exceptions.MisskeyAuthorizeFailedException,
                Req_exceptions.InvalidURL):
            return False

    def del_user(self, user_pos: int) -> None:
        if 0 <= user_pos <= len(self.mistconfig["tokens"]):
            if self.mistconfig["default"]["defaulttoken"] is not None:
                if user_pos < self.mistconfig["default"]["defaulttoken"]:
                    self.mistconfig["default"]["defaulttoken"] -= 1
                elif user_pos == self.mistconfig["default"]["defaulttoken"]:
                    self.mistconfig["default"]["defaulttoken"] = None
                self.mistconfig_put()
            self.mistconfig["tokens"].pop(user_pos)
        else:
            raise ValueError("Invalid position.")

    def select_user(self, user_pos: int) -> bool:
        bef_mk = self.mk
        try:
            is_ok = self.connect_mk_instance(self.mistconfig["tokens"][user_pos]["instance"])
            if is_ok:
                self.mk.token = self.mistconfig["tokens"][user_pos]["token"]
                self.nowuser = user_pos
                if self.mistconfig["tokens"][self.nowuser]["name"] == "Fail to get user info":
                    # 名前がadd時に手に入ってなかったときに再取得する奴
                    try:
                        username = self.mk.i()["name"]
                        self.mistconfig["tokens"][self.nowuser]["name"] = username
                    except MisskeyPyExceptions:
                        pass
                return True
            else:
                raise MisskeyPyExceptions
        except (MisskeyPyExceptions,
                Mi_exceptions.MisskeyAuthorizeFailedException):
            self.mk = bef_mk
            return False

    def default_set_user(self, user_pos: int) -> None:
        if 0 <= user_pos <= len(self.mistconfig["tokens"]):
            self.mistconfig["default"]["defaulttoken"] = user_pos
        else:
            raise ValueError("Invalid position.")

    def del_default_user(self) -> None:
        self.mistconfig["default"]["defaulttoken"] = None

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

    def miauth_check(self, mia: MiAuth) -> Union[str, None]:
        try:
            return mia.check()
        except (Mi_exceptions.MisskeyMiAuthFailedException,
                Req_exceptions.HTTPError):
            return None

    def mistconfig_put(self, loadmode: bool = False) -> None:
        filepath = self._getpath("../mistconfig.conf")
        if loadmode:
            with open(filepath, "r") as f:
                self.mistconfig = json.loads(f.read())
        else:
            with open(filepath, "w") as f:
                f.write(json.dumps(self.mistconfig, indent=4))

    @staticmethod
    def _getpath(dirname: str) -> str:
        """相対パスから絶対パスに変える奴"""
        return os_path.abspath(os_path.join(os_path.dirname(__file__), dirname))
