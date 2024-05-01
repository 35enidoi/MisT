from typing import NoReturn
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
        self.inpbx_txt: str = ""
        self.button_names = (CM_T.RETURN.value, CM_T.TOKEN_BUTTON.value,
                             CM_T.INSTANCE_BUTTON.value, "Honi", CM_T.CLEAR_BUTTON.value)
        self.button_funcs = (partial(self.change_window, "NoteView"), self.token,
                             self.instance, partial(self.add_text, "Honi"), self.clear_text)
        self.ok_button = (CM_T.OK.value, self.ok_func)
        self.ok_mode: bool = False
        self.ok_val: str = ""

    def recreate_before(self, view_: ConfigMenuView) -> None:
        self.view = view_
        self.theme = self.msk_.theme

    def recreate_after(self) -> None:
        self.ok_enable(self.ok_mode)
        self.view.txtbx.value = self.txtbx_txt
        self.view.inp_bx.value = self.inpbx_txt

    def on_change_txtbx(self) -> None:
        self.txtbx_txt = self.view.txtbx.value

    def on_change_inpbx(self) -> None:
        self.inpbx_txt = self.view.inp_bx.value

    def token(self) -> None:
        self.view.popup(CM_T.TOKEN_QUESTION.value,
                        [CM_T.TOKEN_SEL_0.value, CM_T.RETURN.value],
                        self.token_sel)

    def instance(self) -> None:
        self.ok_val = "instance"
        self.add_text(CM_T.CHANGE_INSTANCE_HINT.value)
        self.ok_enable(True)

    def token_sel(self, arg: int) -> None:
        if arg == 0:
            # set token
            self.ok_val = "tokenset"
            self.add_text(CM_T.TOKEN_SET_WRITE_PLS.value)
            self.ok_enable(True)
        elif arg == 1:
            # Return
            pass

    def clear_text(self) -> None:
        self.view.txtbx.value = ""

    def ok_func(self) -> None:
        text = str(self.view.inp_bx.value)
        self.view.inp_bx.value = ""
        if self.ok_val == "tokenset":
            # token set
            self.add_text("mizissoudesu!!!")
            self.add_text(text)
        elif self.ok_val == "instance":
            # instance set
            is_ok = self.msk_.create_mk_instance(text)
            if is_ok:
                self.add_text(CM_T.OK_INSTANCE_CONNECT.value)
            else:
                self.add_text(CM_T.OK_INSTANCE_CONNECT_FAIL.value)
        self.ok_enable(False)

    def add_text(self, *arg: str) -> None:
        for i in arg:
            self.view.txtbx.value += i+"\n"

    def ok_enable(self, _enable: bool) -> None:
        self.ok_mode = _enable
        if not _enable:
            # okじゃない！
            if self.view._focus < len(self.view.buttons)-1:
                self.view.switch_focus(self.view.layout, 0, 0)
        else:
            # okだ...
            if self.view._focus <= len(self.view.buttons):
                self.view.switch_focus(self.view.layout, 0, len(self.view.buttons)+1)
        for i in self.view.buttons:
            i.disabled = _enable
        self.view.inp_bx.disabled = not _enable
        self.view.ok_button.disabled = not _enable

    @staticmethod
    def change_window(target_name: str) -> NoReturn:
        raise NextScene(target_name)
