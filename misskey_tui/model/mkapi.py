from os import path as os_path
from typing import Union, Callable, TypeVar, Any, Literal, cast

from requests import exceptions as Req_exceptions
from misskey import (
    Misskey,
    MiAuth,
    exceptions as Mi_exceptions,
    enum as Mi_enum
)

from misskey_tui.enum.mkapis_exceptions import MisskeyPyExceptions
from misskey_tui.enum.events import ConfigUserEvent, ConfigUserChangeEventMessage, ConfigUserNoneChangeEventMessage
from misskey_tui.enum.misskeypy_return import Note, User
from misskey_tui.model.mistconfig import Config
from misskey_tui.model.events import config_user_hundler


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
    def __init__(self, config: Config) -> None:
        # ConfigUserEventハンドラ登録
        config_user_hundler.add_handler(self.__config_user_hundler)

        DEFAULT_INSTANCE = "misskey.io"
        self.config = config
        # variable set
        self.__on_instance_changes: list[Callable[[], None]] = []
        self.mk: Union[Misskey, None] = None
        self.__instance: str = DEFAULT_INSTANCE
        self.nowuser: Union[int, None] = None
        if self.config.default_token is not None:
            self.config.select_user(self.config.default_token)
        else:
            self.connect_mk_instance(DEFAULT_INSTANCE)

    @property
    def instance(self) -> str:
        """現在接続しているインスタンス"""
        return self.__instance

    @property
    def is_valid_misskeypy(self) -> bool:
        """misskeypyがちゃんとインスタンス化されているか"""
        return self.mk is not None

    def __config_user_hundler(self, event: ConfigUserEvent) -> None:
        """ConfigUserEventを受け取るハンドラ"""
        match event:
            case ConfigUserNoneChangeEventMessage():
                self.mk = None
            case ConfigUserChangeEventMessage():
                # いったん格納
                bef_mk = self.mk
                try:
                    is_ok = self.connect_mk_instance(event.user.instance)
                    if is_ok:
                        self.mk.token = event.token  # type: ignore connect_mk_instanceがTrueでmkは必ず存在
                        self.nowuser = event.mistconfig_position
                        if event.user.name is None:
                            # 名前がadd時に手に入ってなかったときに再取得する奴
                            try:
                                username = self.mk.i()["name"]  # type: ignore 上と同様
                                self.config.update_user(event.mistconfig_position, name=username)
                            except MisskeyPyExceptions:
                                pass
                    else:
                        # TODO エラー処理
                        pass

                except (MisskeyPyExceptions,
                        Mi_exceptions.MisskeyAuthorizeFailedException):
                    # TODO エラー処理
                    self.mk = bef_mk

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

    def verify_token(self, instance: str, token: str) -> User | None:
        """トークンが有効かどうかを確認するやつ"""
        try:
            mk = Misskey(instance, i=token)
            user = mk.i()
            user = cast(User, user)
            return user
        except MisskeyPyExceptions:
            return None

    def mk_get_tl(
            self,
            tl: Literal["HTL", "LTL", "STL", "GTL"],
            limit: int = 30,
            since_id: str | None = None,
            until_id: str | None = None) -> Union[list[Note], None]:
        """misskeypyのタイムライン取得関数を呼び出すやつ"""
        if self.mk is None:
            return None

        if tl == "HTL":
            return self.misskeypy_wrapper(
                self.mk.notes_timeline,
                limit=limit,
                since_id=since_id,
                until_id=until_id
            )  # type: ignore
        elif tl == "LTL":
            return self.misskeypy_wrapper(
                self.mk.notes_local_timeline,
                limit=limit,
                since_id=since_id,
                until_id=until_id
            )  # type: ignore
        elif tl == "STL":
            return self.misskeypy_wrapper(
                self.mk.notes_hybrid_timeline,
                limit=limit,
                since_id=since_id,
                until_id=until_id
            )  # type: ignore
        elif tl == "GTL":
            return self.misskeypy_wrapper(
                self.mk.notes_global_timeline,
                limit=limit,
                since_id=since_id,
                until_id=until_id
            )  # type: ignore
        else:
            raise ValueError(f"Unknown TL type: {tl}")

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
