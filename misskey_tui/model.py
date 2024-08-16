from copy import deepcopy
from os import path as os_path
from glob import glob
import json
import gettext
from typing import Union, Callable, Final, TypeVar

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

__all__ = ["VERSION", "PROGRAM_NAME", "MkAPIs"]

T = TypeVar("T")
P = TypeVar("P")

# version
# syoumi tekitouni ageteru noha naisyo
VERSION = 0.42

# program name
# kore kasyounanode kaerukanousei takai
PROGRAM_NAME = "MisT"


class MkAPIs():
    """MVVMモデルのMの部分"""
    def __init__(self) -> None:
        DEFAULT_INSTANCE = "misskey.io"
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
        self.__instance: str = DEFAULT_INSTANCE
        self.nowuser: Union[int, None] = None
        if self.mistconfig["default"]["defaulttoken"] is not None:
            self.select_user(self.mistconfig["default"]["defaulttoken"])
        else:
            self.connect_mk_instance(DEFAULT_INSTANCE)

    @property
    def now_user_info(self) -> Union[MistConfig_Kata_Token, None]:
        """現在のユーザーの情報"""
        if self.nowuser is not None:
            return self.mistconfig["tokens"][self.nowuser].copy()
        else:
            return None

    @property
    def users_info(self) -> list[MistConfig_Kata_Token]:
        """ユーザー達の情報"""
        return deepcopy(self.mistconfig["tokens"])

    @property
    def instance(self) -> str:
        """現在接続しているインスタンス"""
        return self.__instance

    @property
    def is_valid_misskeypy(self) -> bool:
        """misskeypyがちゃんとインスタンス化されているか"""
        return self.mk is not None

    @property
    def lang(self) -> str:
        """現在の使用言語"""
        return self.__lang

    @property
    def theme(self) -> str:
        """現在のテーマ"""
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
        """文字の翻訳をする関数

        Parameters
        ----------
        lang: str
            言語の種類

        Raises
        ------
        ValueError
            言語の種類が不適の時

        Note
        ----
        有効な言語の種類は:obj:`valid_langs`にリストで載っています。"""
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
        """接続するインスタンスが変わった時に引数の関数を呼び出すようにする

        Parameters
        ----------
        func: Callable
            呼び出させる関数

        Raises
        ------
        ValueError
            引数が呼び出し不可能(関数ではない)とき"""
        if callable(func):
            self.__on_instance_changes.append(func)
        else:
            raise ValueError("function can`t callable.")

    def connect_mk_instance(self, instance: str) -> bool:
        """接続するインスタンスを変更する

        Parameters
        ----------
        instance: str
            接続するインスタンス

        Returns
        -------
        bool
            接続に成功したかどうか"""
        bef_mk = self.mk
        bef_nowuser = self.nowuser
        bef_instance = self.__instance
        try:
            self.mk = Misskey(instance)
            self.nowuser = None
            self.__instance = instance
            for i in self.__on_instance_changes:
                i()
            return True
        except (MisskeyPyExceptions,
                Req_exceptions.InvalidURL):
            self.nowuser = bef_nowuser
            self.__instance = bef_instance
            self.mk = bef_mk
            return False

    def add_user(self, token: str) -> bool:
        """ユーザーを追加する

        Parameters
        ----------
        token: str
            トークン

        Returns
        -------
        bool
            成功したかどうか"""
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
                Mi_exceptions.MisskeyAuthorizeFailedException):
            return False

    def del_user(self, user_pos: int) -> None:
        """ユーザー情報を消す

        Parameters
        ----------
        user_pos: int
            ユーザー情報の場所

        Raises
        ------
        IndexError
            場所が不適の時"""
        if 0 <= user_pos <= len(self.mistconfig["tokens"]) - 1:
            if self.mistconfig["default"]["defaulttoken"] is not None:
                if user_pos < self.mistconfig["default"]["defaulttoken"]:
                    self.mistconfig["default"]["defaulttoken"] -= 1
                elif user_pos == self.mistconfig["default"]["defaulttoken"]:
                    self.mistconfig["default"]["defaulttoken"] = None
                self.mistconfig_put()
            if self.nowuser is not None:
                if user_pos < self.nowuser:
                    self.nowuser -= 1
                elif user_pos == self.nowuser:
                    del self.mk.token
                    self.nowuser = None
            self.mistconfig["tokens"].pop(user_pos)
        else:
            raise IndexError("Invalid position.")

    def select_user(self, user_pos: int) -> bool:
        """ユーザーを選択する

        Parameters
        ----------
        user_pos: int
            ユーザー情報の場所

        Raises
        ------
        IndexError
            場所が不適の時

        Returns
        -------
        bool
            成功したかどうか"""
        if user_pos < 0 or len(self.mistconfig["tokens"]) <= user_pos:
            raise IndexError("Invalid position.")  # 範囲外

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
                return False

        except (MisskeyPyExceptions,
                Mi_exceptions.MisskeyAuthorizeFailedException):
            self.mk = bef_mk
            return False

    def default_set_user(self, user_pos: int) -> None:
        """デフォルトユーザーに指定する

        Parameters
        ----------
        user_pos: int
            ユーザー情報の場所

        Raises
        ------
        IndexError
            場所が不適の時
        """
        if 0 <= user_pos <= len(self.mistconfig["tokens"]) - 1:
            self.mistconfig["default"]["defaulttoken"] = user_pos
        else:
            raise IndexError("Invalid position.")

    def del_default_user(self) -> None:
        """デフォルトユーザーの指定を消す

        Note
        ----
        デフォルトユーザーがいない場合、何も起きません。実際同じ値代入してるだけ。実際そう。"""
        self.mistconfig["default"]["defaulttoken"] = None

    def get_miauth(self) -> MiAuth:
        """miauthを取得するやつ"""
        permissions = [Mi_enum.Permissions.WRITE_NOTES.value,
                       Mi_enum.Permissions.READ_ACCOUNT.value,
                       Mi_enum.Permissions.WRITE_ACCOUNT.value,
                       Mi_enum.Permissions.READ_REACTIONS.value,
                       Mi_enum.Permissions.WRITE_REACTIONS.value,
                       Mi_enum.Permissions.READ_MESSAGING.value,
                       Mi_enum.Permissions.WRITE_MESSAGING.value,
                       Mi_enum.Permissions.READ_NOTIFICATIONS.value,
                       Mi_enum.Permissions.WRITE_NOTIFICATIONS.value]

        return MiAuth(address=self.__instance, name=PROGRAM_NAME, permission=permissions)

    def mistconfig_put(self, loadmode: bool = False) -> None:
        """mistconfigの情報を保存させる"""
        filepath = self._getpath("../mistconfig.conf")
        if loadmode:
            with open(filepath, "r") as f:
                self.mistconfig = json.loads(f.read())
        else:
            with open(filepath, "w") as f:
                f.write(json.dumps(self.mistconfig, indent=4))

    @staticmethod
    def misskeypy_wrapper(msk_func: Callable[[P], T], **kargs: P) -> Union[T, None]:
        """
        misskey.pyの例外が発生したらNoneを返すやーつ"""
        if callable(msk_func):
            try:
                return msk_func(**kargs)
            except MisskeyPyExceptions:
                return None
        else:
            raise TypeError(f"{msk_func} is not callable.")

    @staticmethod
    def _getpath(dirname: str) -> str:
        """相対パスから絶対パスに変える奴"""
        return os_path.abspath(os_path.join(os_path.dirname(__file__), dirname))
