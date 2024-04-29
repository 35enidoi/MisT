from functools import partial
from typing import Union

from asciimatics.exceptions import NextScene

from misskey_tui.model import MkAPIs
from misskey_tui.scenes.noteview.view import NoteView
from misskey_tui.textenums import NV_T
from misskey_tui.abstract.viewmodel import AbstractViewModel


class NoteViewModel(AbstractViewModel):
    """NoteViewのViewModel"""
    def __init__(self, msk: MkAPIs) -> None:
        # modelの保存
        self.msk_ = msk
        # 変数作成
        self.txtbx_txt: str = NV_T.WELCOME_MESSAGE.value
        self.notes: Union[list[dict], None] = []
        self.notes_point: int = 0
        self.TL = "HTL"
        self.theme = self.msk_.theme
        self.button_names = (NV_T.QUIT.value, "Change", "Config")
        self.button_funcs = (self.quit_question, self.change_test, partial(self.change_window, "ConfigMenu"))
        # 型ヒント
        self.view: NoteView

    def recreate_before(self, view_: NoteView) -> None:
        self.view = view_
        self.theme = self.msk_.theme

    def recreate_after(self) -> None:
        self.view.textbox.value = self.txtbx_txt

    def on_change_txtbx(self) -> None:
        self.txtbx_txt = self.view.textbox.value

    def change_test(self) -> None:
        self.view.textbox.value += "\nHoni"

    def quit_question(self) -> None:
        self.view.popup("Quit?", [NV_T.OK.value, NV_T.RETURN.value], self.quit)

    def quit(self, arg: int) -> None:
        if arg == 0:
            self.view.quit()

    @staticmethod
    def change_window(target_name: str) -> None:
        raise NextScene(target_name)
