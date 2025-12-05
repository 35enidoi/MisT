from copy import deepcopy
from os import path as os_path
from typing import Union, Callable, TypeVar, Any

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
    MistConfig_Kata_Token
)
from misskey_tui.model.mistconfig import MisTConfig


# TODO  mistconfigの削除
# TODO  langの削除

__all__ = ["PROGRAM_NAME", "MkAPIs"]

T = TypeVar("T")
P = TypeVar("P")

# program name
# kore kasyounanode kaerukanousei takai
PROGRAM_NAME = "MisT"


class MkAPIs():
    """MVVMモデルのMの部分"""
    def __init__(self, config: MisTConfig) -> None:
        DEFAULT_INSTANCE = "misskey.io"
        self.config = config
        # variable set
        self.__theme = self.config.default_theme
        self.__on_instance_changes: list[Callable[[], None]] = []
        self.mk: Union[Misskey, None] = None
        self.__instance: str = DEFAULT_INSTANCE
        self.nowuser: Union[int, None] = None
        if self.config.default_token is not None:
            user_pos = self.config.token_position_check(self.config.default_token)
            if user_pos is not None:
                self.select_user(user_pos)
        else:
            self.connect_mk_instance(DEFAULT_INSTANCE)

    @property
    def now_user_info(self) -> Union[MistConfig_Kata_Token, None]:
        """現在のユーザーの情報"""
        if self.nowuser is not None:
            return self.config.tokens[self.nowuser]
        else:
            return None

    @property
    def users_info(self) -> list[MistConfig_Kata_Token]:
        """ユーザー達の情報"""
        return deepcopy(self.config["tokens"])

    @property
    def instance(self) -> str:
        """現在接続しているインスタンス"""
        return self.__instance

    @property
    def is_valid_misskeypy(self) -> bool:
        """misskeypyがちゃんとインスタンス化されているか"""
        return self.mk is not None

    @property
    def theme(self) -> str:
        """現在のテーマ"""
        return self.__theme

    @theme.setter
    def theme(self, val: str) -> None:
        if val in THEMES:
            self.__theme = val
            self.config.default_theme = val
            self.config.save_config()
        else:
            raise ValueError(f"theme `{val}` not in THEMES.")

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
        if self.mk is None:
            # TODO エラーを投げるようにする
            return False
        try:
            self.mk.token = token
            try:
                name = self.mk.i()["name"]
            except MisskeyPyExceptions:
                name = "Fail to get user info"
            self.config["tokens"].append(MistConfig_Kata_Token(name=name,
                                                                   instance=self.__instance,
                                                                   token=token,
                                                                   reacdeck=[]))
            return True
        except (MisskeyPyExceptions,
                Mi_exceptions.MisskeyAuthorizeFailedException):
            return False

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
        # 範囲内かどうか調べる
        if user_pos < 0 or len(self.config["tokens"]) <= user_pos:
            raise IndexError("Invalid position.")

        # いったん格納
        bef_mk = self.mk
        try:
            is_ok = self.connect_mk_instance(self.config["tokens"][user_pos]["instance"])
            if is_ok:
                self.mk.token = self.config["tokens"][user_pos]["token"]  # type: ignore connect_mk_instanceがTrueでmkは必ず存在
                self.nowuser = user_pos
                if self.config["tokens"][self.nowuser]["name"] == "Fail to get user info":
                    # 名前がadd時に手に入ってなかったときに再取得する奴
                    try:
                        username = self.mk.i()["name"]  # type: ignore 上と同様
                        self.config["tokens"][self.nowuser]["name"] = username
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
        if 0 <= user_pos <= len(self.config["tokens"]) - 1:
            self.config["default"]["defaulttoken"] = user_pos
        else:
            raise IndexError("Invalid position.")

    def del_default_user(self) -> None:
        """デフォルトユーザーの指定を消す

        Note
        ----
        デフォルトユーザーがいない場合、何も起きません。実際同じ値代入してるだけ。実際そう。"""
        self.config.default_token = None

    def get_miauth(self) -> MiAuth:
        """miauthを取得するやつ"""
        return MiAuth(address=self.__instance, name=PROGRAM_NAME, permission=[
            Mi_enum.Permissions.WRITE_NOTES.value,
            Mi_enum.Permissions.READ_ACCOUNT.value,
            Mi_enum.Permissions.WRITE_ACCOUNT.value,
            Mi_enum.Permissions.READ_REACTIONS.value,
            Mi_enum.Permissions.WRITE_REACTIONS.value,
            Mi_enum.Permissions.READ_MESSAGING.value,
            Mi_enum.Permissions.WRITE_MESSAGING.value,
            Mi_enum.Permissions.READ_NOTIFICATIONS.value,
            Mi_enum.Permissions.WRITE_NOTIFICATIONS.value
        ])

    @staticmethod
    def misskeypy_wrapper(msk_func: Callable[..., T], *args: Any, **kwargs: Any) -> Union[T, None]:
        """
        misskey.pyの例外が発生したらNoneを返すやーつ"""
        if callable(msk_func):
            try:
                return msk_func(*args, **kwargs)
            except MisskeyPyExceptions:
                return None
        else:
            raise TypeError(f"{msk_func} is not callable.")

    @staticmethod
    def _getpath(dirname: str) -> str:
        """プロジェクトのルートディレクトリからのパスを取得する"""
        project_root = os_path.abspath(os_path.join(os_path.dirname(__file__), "../../"))

        return os_path.abspath(os_path.join(project_root, dirname))
