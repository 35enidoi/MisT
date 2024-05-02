from typing import NoReturn
from functools import partial

from asciimatics.exceptions import NextScene, ResizeScreenError

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
        self.button_names: tuple[str, ...]
        self.button_funcs = (partial(self.change_window, "NoteView"), self.token, self.instance,
                             self.theme_, self.language, self.clear_text)
        self.ok_button = (CM_T.OK.value, self.ok_func)
        self.ok_mode: bool = False
        self.ok_val: str = ""

    def recreate_before(self, view_: ConfigMenuView) -> None:
        self.button_names = (CM_T.RETURN.value, CM_T.TOKEN_BUTTON.value, CM_T.INSTANCE_BUTTON.value,
                             CM_T.THEME_BUTTON.value, CM_T.LANGUAGE_BUTTON.value, CM_T.CLEAR_BUTTON.value)
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

    def language(self) -> None:
        self.view.popup(CM_T.LANGUAGE_QUESTION.value,
                        [*self.msk_.valid_langs, CM_T.LANGUAGE_RESET.value, CM_T.RETURN.value],
                        self.language_sel)

    def instance(self) -> None:
        self.ok_val = "instance"
        self.add_text(CM_T.CHANGE_INSTANCE_HINT.value)
        self.ok_enable(True)

    def theme_(self) -> None:
        self.view.popup(CM_T.THEME_QUESTION.value,
                        [CM_T.THEME_DEFAULT.value, CM_T.THEME_MONO.value,
                         CM_T.THEME_GREEN.value, CM_T.THEME_BRIGHT.value,
                         CM_T.RETURN.value],
                        self.theme_sel)

    def token_sel(self, arg: int) -> None:
        if arg == 0:
            # set token
            self.ok_val = "tokenset"
            self.add_text(CM_T.TOKEN_SET_WRITE_PLS.value)
            self.ok_enable(True)
        elif arg == 1:
            # Return
            pass

    def language_sel(self, arg: int) -> None:
        if arg <= len(self.msk_.valid_langs)-1:
            # sel lang
            lang = self.msk_.valid_langs[arg]
        elif arg == len(self.msk_.valid_langs):
            # reset lang
            lang = ""
        elif arg == len(self.msk_.valid_langs)+1:
            # return
            return
        self.msk_.translation(lang)
        raise ResizeScreenError("honi", self.view._scene)

    def theme_sel(self, arg: int) -> None:
        if arg == 4:
            # Return
            return
        else:
            # select theme
            theme = ("default", "monochrome", "green", "bright")[arg]
            self.msk_.theme = theme
            self.view.set_theme(theme)
            raise ResizeScreenError("honi", self.view._scene)

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
