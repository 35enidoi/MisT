from os import path
from copy import copy
from glob import glob
from typing import Optional
import gettext
import json

from asciimatics.widgets.utilities import THEMES

from misskey_tui.enum.mkapis_enum import MistConfig_Kata, MistConfig_Kata_Default, MistConfig_Kata_Token
from misskey_tui.enum.events import ConfigUserDelEventMessage, ConfigUserNoneChangeEventMessage, ConfigUserChangeEventMessage
from misskey_tui.model.events import config_user_hundler
from misskey_tui.util import get_path


class MisTConfig:
    __settings: MistConfig_Kata
    __valid_langs: tuple[str, ...]
    __current_user: int | None
    __config_file_path: str

    def __init__(self, version: float):
        # 言語ファイルの読み込み
        self.__valid_langs = tuple(path.basename(path.dirname(i)) for i in glob(get_path("./locale/*/LC_MESSAGES")))

        # Configファイルの読み込み
        self.__config_file_path = get_path("./mistconfig.conf")
        if path.exists(self.__config_file_path):
            self.__settings = self.load_config()
            if self.__settings.version < version:
                self.__settings = self.__setting_init(version)
                self.save_config()
        else:
            self.__settings = self.__setting_init(version)

        # MisTConfigから色々情報持ってくる
        self.__current_user = self.__settings.default.defaulttoken
        self.translation(self.__settings.default.lang)

    @property
    def valid_langs(self) -> tuple[str, ...]:
        return self.__valid_langs

    @property
    def lang(self) -> str | None:
        return self.__settings.default.lang

    @property
    def version(self) -> float:
        return self.__settings.version

    @property
    def default_token(self) -> int | None:
        if (token_pos := self.__settings.default.defaulttoken) is None:
            return None
        else:
            return token_pos

    @property
    def users(self) -> list[MistConfig_Kata_Token]:
        return self.__settings.tokens.copy()

    @property
    def current_user(self) -> MistConfig_Kata_Token | None:
        return copy(self.__settings.tokens[self.__current_user]) if self.__current_user is not None else None

    @property
    def theme(self) -> str:
        return self.__settings.default.theme

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

    def add_user(self, name: str | None, instance: str, token: str, reacdeck: list[str]) -> None:
        """ユーザーを追加する

        Parameters
        ----------
        token: str
            トークン"""
        self.__settings.tokens.append(
            MistConfig_Kata_Token(
                name=name,
                instance=instance,
                token=token,
                reacdeck=reacdeck
                )
            )

        self.save_config()

    def update_user(self, user_pos: int, *, name: Optional[str] = None, reacdeck: Optional[list[str]] = None) -> None:
        """ユーザー情報を更新する

        Parameters
        ----------
        user_pos: int
            ユーザー情報の場所
        token: str
            トークン

        Raises
        ------
        IndexError
            場所が不適の時"""
        # 更新対象の位置が有効範囲か検査
        if 0 <= user_pos <= len(self.__settings.tokens) - 1:
            # 実際に対象ユーザー情報をリストから更新
            current_info = self.__settings.tokens[user_pos]

            if name is not None:
                current_info.name = name
            if reacdeck is not None:
                current_info.reacdeck = reacdeck

            self.__settings.tokens[user_pos] = current_info

            self.save_config()
        else:
            # 範囲外の位置なら例外を送出
            raise IndexError("Invalid position.")

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
        if 0 <= user_pos <= len(self.__settings.tokens) - 1:
            # デフォルトユーザー設定への影響を調整
            if self.__settings.default.defaulttoken is not None:
                # 削除位置がデフォルト位置より前ならインデックスを詰める
                if user_pos < self.__settings.default.defaulttoken:
                    self.__settings.default.defaulttoken -= 1
                # デフォルト本人を削除するならデフォルト解除
                elif user_pos == self.__settings.default.defaulttoken:
                    self.__settings.default.defaulttoken = None
                # 変更を設定ファイルへ保存
                self.save_config()

            # 現在選択中ユーザーへの影響を調整
            if self.__current_user is not None:
                # 削除位置が現在選択中位置より前ならインデックスを詰める
                if user_pos < self.__current_user:
                    self.__current_user -= 1
                # 現在選択中本人を削除するならログアウト扱いにする
                elif user_pos == self.__current_user:
                    self.__current_user = None
                    config_user_hundler.fire(ConfigUserNoneChangeEventMessage())

            # 実際に対象ユーザー情報をリストから削除
            self.__settings.tokens.pop(user_pos)

            config_user_hundler.fire(ConfigUserDelEventMessage(
                mistconfig_position=user_pos
            ))

            self.save_config()

        else:
            # 範囲外の位置なら例外を送出
            raise IndexError("Invalid position.")

    def select_user(self, user_pos: int) -> None:
        """ユーザーを選択する

        Parameters
        ----------
        user_pos: int
            ユーザー情報の場所

        Raises
        ------
        IndexError
            場所が不適の時"""
        # 範囲内かどうか調べる
        if user_pos < 0 or len(self.__settings.tokens) <= user_pos:
            raise IndexError("Invalid position.")
        else:
            self.__current_user = user_pos
            user = MistConfig_Kata_Token(
                name=self.__settings.tokens[user_pos].name,
                reacdeck=self.__settings.tokens[user_pos].reacdeck,
                instance=self.__settings.tokens[user_pos].instance,
                token=self.__settings.tokens[user_pos].token
            )
            config_user_hundler.fire(ConfigUserChangeEventMessage(
                mistconfig_position=user_pos,
                user=user
            ))

    def logout_user(self) -> None:
        """ユーザーをログアウトする"""
        self.__current_user = None
        config_user_hundler.fire(ConfigUserNoneChangeEventMessage())

    def set_default_user(self, user: MistConfig_Kata_Token | None) -> None:
        if user is None:
            self.__settings.default.defaulttoken = None
        else:
            user_position = self.token_position_check(user)
            if user_position is None:
                raise ValueError("The user is not registered.")
            if 0 <= user_position <= len(self.__settings.tokens) - 1:
                self.__settings.default.defaulttoken = user_position
            else:
                raise IndexError("Invalid position.")

        self.save_config()

    def set_theme(self, theme: str) -> None:
        if theme in THEMES:
            self.__settings.default.theme = theme
            self.save_config()
        else:
            raise ValueError(f"theme `{theme}` not in THEMES.")

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
        self.__settings.default.lang = lang
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
        for i, v in enumerate(self.__settings.tokens):
            if v.token == token.token:
                return i

        return None  # 存在しない場合はNoneを返す
