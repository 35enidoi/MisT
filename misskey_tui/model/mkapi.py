from copy import deepcopy
from os import path as os_path
import json
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
        # 削除対象の位置が有効範囲か検査
        if 0 <= user_pos <= len(self.mistconfig["tokens"]) - 1:
            # デフォルトユーザー設定への影響を調整
            if self.mistconfig["default"]["defaulttoken"] is not None:
                # 削除位置がデフォルト位置より前ならインデックスを詰める
                if user_pos < self.mistconfig["default"]["defaulttoken"]:
                    self.mistconfig["default"]["defaulttoken"] -= 1
                # デフォルト本人を削除するならデフォルト解除
                elif user_pos == self.mistconfig["default"]["defaulttoken"]:
                    self.mistconfig["default"]["defaulttoken"] = None
                # 変更を設定ファイルへ保存
                self.mistconfig_put()

            # 現在選択中ユーザーへの影響を調整
            if self.nowuser is not None:
                # 削除位置が現在位置より前ならインデックスを詰める
                if user_pos < self.nowuser:
                    self.nowuser -= 1
                # 現在のユーザー本人を削除ならログアウト相当
                elif user_pos == self.nowuser:
                    # ログアウト処理
                    if self.mk is not None:
                        del self.mk.token

                    self.nowuser = None

            # 実際に対象ユーザー情報をリストから削除
            self.mistconfig["tokens"].pop(user_pos)

        else:
            # 範囲外の位置なら例外を送出
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
        # 範囲内かどうか調べる
        if user_pos < 0 or len(self.mistconfig["tokens"]) <= user_pos:
            raise IndexError("Invalid position.")

        # いったん格納
        bef_mk = self.mk
        try:
            is_ok = self.connect_mk_instance(self.mistconfig["tokens"][user_pos]["instance"])
            if is_ok:
                self.mk.token = self.mistconfig["tokens"][user_pos]["token"]  # type: ignore connect_mk_instanceがTrueでmkは必ず存在
                self.nowuser = user_pos
                if self.mistconfig["tokens"][self.nowuser]["name"] == "Fail to get user info":
                    # 名前がadd時に手に入ってなかったときに再取得する奴
                    try:
                        username = self.mk.i()["name"]  # type: ignore 上と同様
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

    def mistconfig_put(self, loadmode: bool = False) -> None:
        """mistconfigの情報を保存させる"""
        filepath = self._getpath("./mistconfig.conf")
        if loadmode:
            with open(filepath, "r") as f:
                self.mistconfig = json.loads(f.read())
        else:
            with open(filepath, "w") as f:
                f.write(json.dumps(self.mistconfig, indent=4))

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
