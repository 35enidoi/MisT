from functools import partial

from asciimatics.exceptions import NextScene

from misskey_tui.model import MkAPIs
from misskey_tui.scenes.configmenu.view import ConfigMenuView
from misskey_tui.textenums import CM_T
from misskey_tui.abstract.viewmodel import AbstractViewModel


class ConfigMenuModel(AbstractViewModel):
    def __init__(self, msk: MkAPIs) -> None:
        # modelの保存
        self.msk_ = msk
        # 変数作成
        self.theme = self.msk_.theme
        self.view: ConfigMenuView
        self.txtbx_txt: str = ""
        self.button_names = (CM_T.RETURN.value, "Honi", "Clear")
        self.button_funcs = (partial(self.change_window, "NoteView"), partial(self.add_text, "Honi"), self.clear_text)

    def recreate_before(self, view_: ConfigMenuView) -> None:
        self.view = view_
        self.theme = self.msk_.theme

    def recreate_after(self) -> None:
        self.view.txtbx.value = self.txtbx_txt

    def add_text(self, *arg: str) -> None:
        self.txtbx_txt += "\n"
        for i in arg:
            self.txtbx_txt += i+"\n"
        self.txtbx_txt = self.txtbx_txt.strip()
        self.view.txtbx.value = self.txtbx_txt

    def clear_text(self) -> None:
        self.txtbx_txt = ""
        self.view.txtbx.value = self.txtbx_txt

    @staticmethod
    def change_window(target_name: str) -> None:
        raise NextScene(target_name)
