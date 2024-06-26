from typing import Callable
from functools import partial

from asciimatics.exceptions import ResizeScreenError

from misskey_tui.model import MkAPIs
from misskey_tui.scenes.configmenu.view import ConfigMenuView
from misskey_tui.textenums import CM_T
from misskey_tui.abstract import AbstractViewModel


class ConfigMenuModel(AbstractViewModel):
    def __init__(self, msk: MkAPIs) -> None:
        # modelの保存
        self.msk_ = msk
        # 変数作成
        self.theme = self.msk_.theme
        self.view: ConfigMenuView
        self.txtbx_txt: str = ""
        self.inpbx_txt: str = ""
        self.ok_selections: dict[str, Callable[[str], None]] = {
            "tokenset": self.token_on_ok,
            "instance": self.instance_on_ok
        }
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
                        [CM_T.TOKEN_SEL_0.value, CM_T.TOKEN_SEL_1.value, CM_T.RETURN.value],
                        self.token_sel)

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

    def language(self) -> None:
        self.view.popup(CM_T.LANGUAGE_QUESTION.value,
                        [*self.msk_.valid_langs, CM_T.LANGUAGE_RESET.value, CM_T.RETURN.value],
                        self.language_sel)

    def current(self) -> None:
        self.add_text(CM_T.CURRENT_INSTANCE.value + ": " + self.msk_.instance)
        if self.msk_.now_user_info is not None:
            self.add_text(CM_T.CURRENT_TOKEN.value + ": " + CM_T.CURRENT_VALID.value,
                          CM_T.CURRENT_NAME.value + ": " + self.msk_.now_user_info["name"],
                          CM_T.CURRENT_TOKENID.value + ": " + self.msk_.now_user_info["token"][:8] + "...")
        else:
            self.add_text(CM_T.CURRENT_TOKEN.value + ": " + CM_T.CURRENT_INVALID.value)

    def token_sel(self, arg: int) -> None:
        if arg == 0:
            # set token
            self.ok_val = "tokenset"
            self.add_text(CM_T.TOKEN_SET_WRITE_PLS.value)
            self.ok_enable(True)
        elif arg == 1:
            # Select
            if len(self.msk_.users_info) != 0:
                self.token_on_select(0)
            else:
                self.view.popup(CM_T.TOKEN_SEL_1_NO_USER.value, CM_T.OK.value)
        elif arg == 2:
            # Return
            pass

    def token_on_select(self, position: int) -> None:
        BUTTONS = (CM_T.TOKEN_USER_SEL.value, CM_T.TOKEN_NOW_USER_L.value,
                   CM_T.TOKEN_NOW_USER_R.value, CM_T.RETURN.value)
        userinfo = self.msk_.users_info[position]
        text = "\n".join([
            f"<{position+1}/{len(self.msk_.users_info)}> " + CM_T.TOKEN_NOW_USER_INFO.value,
            CM_T.TOKEN_USER_INSTANCE.value + f": {userinfo['instance']}",
            CM_T.TOKEN_USER_NAME.value + f": {userinfo['name']}",
            CM_T.TOKEN_USER_TOKEN.value + f": {userinfo['token'][:8]}..."
        ])
        self.view.popup(
            txt=text,
            button=BUTTONS,
            on_close=partial(self.on_token_select, pos=position)
        )

    def on_token_select(self, arg: int, pos: int) -> None:
        if arg == 0:
            # select
            self.select_token_pop(pos=pos)
        elif arg == 1:
            # L
            if pos - 1 != -1:
                pos -= 1
            self.token_on_select(pos)
        elif arg == 2:
            # R
            if pos + 1 != len(self.msk_.users_info):
                pos += 1
            self.token_on_select(pos)
        elif arg == 3:
            # Return
            pass

    def select_token_pop(self, pos: int) -> None:
        CHOICES = (CM_T.TOKEN_USER_SEL.value, CM_T.TOKEN_USER_SELECT_DELETE.value,
                   CM_T.TOKEN_USER_DEFAULT_SET.value, CM_T.RETURN.value)
        userinfo = self.msk_.users_info[pos]
        text = "\n".join([
            CM_T.TOKEN_SELECTED_INFO.value,
            CM_T.TOKEN_USER_INSTANCE.value + f": {userinfo['instance']}",
            CM_T.TOKEN_USER_NAME.value + f": {userinfo['name']}",
            CM_T.TOKEN_USER_TOKEN.value + f": {userinfo['token'][:8]}..."
        ])
        self.view.popup(
            txt=text,
            button=CHOICES,
            on_close=partial(self.on_select_token_pop, pos=pos)
        )

    def on_select_token_pop(self, arg: int, pos: int) -> None:
        if arg == 0:
            # Set
            is_ok = self.msk_.select_user(pos)
            if is_ok:
                text = CM_T.TOKEN_SELECT_SUCCESS.value
            else:
                text = CM_T.TOKEN_SELECT_FAIL.value
            self.view.popup(text, ["Ok"])
        elif arg == 1:
            # Delete
            def _del_check(is_ok: int):
                if is_ok == 1:
                    # 消す
                    self.msk_.del_user(pos)
                    self.add_text(CM_T.TOKEN_DELETED.value)
                else:
                    pass

            self.view.popup(
                txt=CM_T.TOKEN_DELETE_CHECK.value,
                button=[CM_T.NO.value, CM_T.YES.value],
                on_close=_del_check)
        elif arg == 2:
            # Default Set
            self.msk_.default_set_user(pos)
            self.add_text(CM_T.TOKEN_DEFAULT_SETTED.value)
        elif arg == 3:
            # Return
            pass

    def token_on_ok(self, text: str) -> None:
        is_ok = self.msk_.add_user(text)
        if is_ok:
            self.msk_.select_user(-1)
            self.add_text("TOKEN check successful! :)")
        else:
            self.add_text("TOKEN check fail :(")

    def instance_on_ok(self, text: str) -> None:
        is_ok = self.msk_.connect_mk_instance(text)
        if is_ok:
            self.add_text(CM_T.OK_INSTANCE_CONNECT.value)
        else:
            self.add_text(CM_T.OK_INSTANCE_CONNECT_FAIL.value)

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

    def show_now_info(self) -> None:
        self.add_text("Current Instance: " + self.msk_.instance)
        if self.msk_.now_user_info is not None:
            self.add_text("TOKEN: Valid")
            self.add_text("Name: " + self.msk_.now_user_info["name"])
            self.add_text("TOKENId: " + self.msk_.now_user_info["token"][:8] + "...")
        else:
            self.add_text("TOKEN:" + "Invalid")

    def clear_text(self) -> None:
        self.view.txtbx.value = ""

    def ok_func(self) -> None:
        text = str(self.view.inp_bx.value)
        self.view.inp_bx.value = ""
        self.ok_selections[self.ok_val](text)
        self.ok_val = ""
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
