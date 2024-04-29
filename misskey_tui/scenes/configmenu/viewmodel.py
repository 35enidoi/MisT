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
        self.button_names = (CM_T.RETURN.value,
                             "Honi", "Clear")
        self.button_funcs = (partial(self.change_window, "NoteView"),
                             partial(self.add_text, "Honi"), self.clear_text)
        self.ok_button = (CM_T.OK.value, self.ok_func)
        self.ok_mode: bool = False
        self.ok_val: str = ""

    def recreate_before(self, view_: ConfigMenuView) -> None:
        self.view = view_
        self.theme = self.msk_.theme

    def recreate_after(self) -> None:
        self.ok_disable(self.ok_mode)
        self.view.txtbx.value = self.txtbx_txt

    def clear_text(self) -> None:
        self.txtbx_txt = ""
        self.view.txtbx.value = self.txtbx_txt

    def ok_func(self) -> None:
        pass

    def add_text(self, *arg: str) -> None:
        self.txtbx_txt += "\n"
        for i in arg:
            self.txtbx_txt += i+"\n"
        self.txtbx_txt = self.txtbx_txt.strip()
        self.view.txtbx.value = self.txtbx_txt

    def ok_disable(self, _disable: bool):
        for i in self.view.buttons:
            i.disabled = _disable
        self.view.inp_bx.disabled = not _disable
        self.view.ok_button.disabled = not _disable

    @staticmethod
    def change_window(target_name: str) -> None:
        raise NextScene(target_name)
