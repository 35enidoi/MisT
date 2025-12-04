from os import path
from glob import glob
import gettext
import json

from asciimatics.widgets.utilities import THEMES

from misskey_tui.enum.mkapis_enum import MistConfig_Kata, MistConfig_Kata_Default, MistConfig_Kata_Token
from misskey_tui.enum.events import UserChangeEventMessageUserChange, UserChangeEventMessageUserNone
from misskey_tui.model.events import EventHandler
from misskey_tui.util import get_path


class MisTConfig:
    __settings: MistConfig_Kata
    __valid_langs: tuple[str, ...]
    __current_user: int | None

    def __init__(self, version: float):
        # 言語ファイルの読み込み
        self.__valid_langs = tuple(path.basename(path.dirname(i)) for i in glob(get_path("./locale/*/LC_MESSAGES")))
        # Configファイルの読み込み
        self.__config_file_path = get_path("./mistconfig.conf")
        if path.exists(self.__config_file_path):
            self.__settings = self.load_config()
            if self.__settings["version"] < version:
                self.__settings = self.__setting_init(version)
                self.save_config()
        else:
            self.__settings = self.__setting_init(version)
        # MisTConfigから色々情報持ってくる
        self.__current_user = self.__settings["default"]["defaulttoken"]
        self.translation(self.__settings["default"]["lang"])

    @property
    def valid_langs(self) -> tuple[str, ...]:
        return self.__valid_langs

    @property
    def lang(self) -> str | None:
        return self.__settings["default"]["lang"]

    @property
    def version(self) -> float:
        return self.__settings["version"]

    @property
    def default_token(self) -> int | None:
        if (token_pos := self.__settings["default"]["defaulttoken"]) is None:
            return None
        else:
            return token_pos

    @default_token.setter
    def default_token(self, token: MistConfig_Kata_Token | None) -> None:
        if token is None:
            self.__settings["default"]["defaulttoken"] = None
        else:
            pos = self.token_position_check(token)
            if pos is not None:
                self.__settings["default"]["defaulttoken"] = pos
            else:
                raise ValueError("The specified token does not exist in the config.")

    @property
    def default_theme(self) -> str:
        return self.__settings["default"]["theme"]

    @default_theme.setter
    def default_theme(self, theme: str) -> None:
        if theme not in THEMES:
            raise ValueError(f"theme `{theme}` is invalid.")
        self.__settings["default"]["theme"] = theme
        self.save_config()

    @property
    def tokens(self) -> list[MistConfig_Kata_Token]:
        return self.__settings["tokens"].copy()

    @property
    def current_user(self) -> int | None:
        return self.__current_user

    @current_user.setter
    def current_user(self, pos: int | None) -> None:
        if pos is None:
            message = UserChangeEventMessageUserNone(
                mistconfig_position=None,
                user_name=None,
                reacdeck=None,
                instance=None
            )
            EventHandler.fire_user_change(message)

            self.__current_user = None
        elif 0 <= pos < len(self.__settings["tokens"]):
            token = self.__settings["tokens"][pos]
            message = UserChangeEventMessageUserChange(
                mistconfig_position=pos,
                user_name=token["name"],
                reacdeck=token["reacdeck"],
                instance=token["instance"]
            )
            EventHandler.fire_user_change(message)

            self.__current_user = pos
        else:
            # 範囲外の値が来た場合は例外送出
            raise IndexError("current_user index is out of range.")

    def __config_hundler(self, event: ):

    def __setting_init(self, version: float) -> MistConfig_Kata:
        return MistConfig_Kata(
            version=version,
            default=MistConfig_Kata_Default(
                theme="default",
                lang=None,
                defaulttoken=None
            ),
            tokens=[]
        )

    def add_user(self, name: str, instance: str, token: str, reacdeck: list[str]) -> None:
        """ユーザーを追加する

        Parameters
        ----------
        token: str
            トークン"""
        self.__settings["tokens"].append(
            MistConfig_Kata_Token(name=name,
                                  instance=instance,
                                  token=token,
                                  reacdeck=reacdeck))

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
        if 0 <= user_pos <= len(self.__settings["tokens"]) - 1:
            # デフォルトユーザー設定への影響を調整
            if self.__settings["default"]["defaulttoken"] is not None:
                # 削除位置がデフォルト位置より前ならインデックスを詰める
                if user_pos < self.__settings["default"]["defaulttoken"]:
                    self.__settings["default"]["defaulttoken"] -= 1
                # デフォルト本人を削除するならデフォルト解除
                elif user_pos == self.__settings["default"]["defaulttoken"]:
                    self.__settings["default"]["defaulttoken"] = None
                # 変更を設定ファイルへ保存
                self.save_config()

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
            self.__settings["tokens"].pop(user_pos)

        else:
            # 範囲外の位置なら例外を送出
            raise IndexError("Invalid position.")

    def load_config(self) -> MistConfig_Kata:
        with open(self.__config_file_path, 'r') as f:
            return json.load(f)

    def save_config(self):
        with open(self.__config_file_path, 'w') as f:
            json.dump(self.__settings, f, indent=4)

    def translation(self, lang: str | None) -> None:
        """文字の翻訳をする関数

        Parameters
        ----------
        lang: str | None
            言語の種類

        Raises
        ------
        ValueError
            言語の種類が不適の時

        Note
        ----
        有効な言語の種類は:obj:`valid_langs`にリストで載っています。"""
        # 翻訳ファイルを配置するディレクトリ
        path_to_locale_dir = get_path("./locale")

        # ちゃんと使えるか確認
        if lang not in self.valid_langs and lang is not None:
            raise ValueError(f"language `{lang}` is invalid.")

        # 保存
        self.__settings["default"]["lang"] = lang
        self.save_config()

        # 翻訳用クラスの設定
        translater = gettext.translation(
            'messages',                          # domain: 辞書ファイルの名前
            localedir=path_to_locale_dir,        # 辞書ファイル配置ディレクトリ
            languages=[lang] if lang else lang,  # 翻訳に使用する言語
            fallback=True                        # .moファイルが見つからなかった時は未翻訳の文字列を出力
        )

        # Pythonの組み込みグローバル領域に_という関数を束縛する
        translater.install()

    def token_position_check(self, token: MistConfig_Kata_Token) -> int | None:
        """トークンの位置を調べる関数

        Parameters
        ----------
        token: MistConfig_Kata_Token
            調べたいトークン

        Returns
        -------
        int | None
            トークンの位置。存在しない場合はNoneを返す"""
        for i, v in enumerate(self.__settings["tokens"]):
            if v["token"] == token["token"]:
                return i

        return None  # 存在しない場合はNoneを返す
