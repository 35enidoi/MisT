from misskey_tui.model import MkAPIs
from misskey_tui.scenes.noteview.view import NoteView
from misskey_tui.textenums import NV_T
from misskey_tui.abstract import AbstractViewModel


class NoteViewModel(AbstractViewModel):
    """NoteViewのViewModel"""
    def __init__(self, msk: MkAPIs) -> None:
        # modelの保存
        self.msk_ = msk
        # 変数作成
        self.txtbx_txt: str = NV_T.WELCOME_MESSAGE.value
        self.notes: list[dict] = []
        self.notes_point: int = 0
        self.TL = "LTL"
        self.theme = self.msk_.theme
        # フック作成
        self.msk_.add_on_change_instance(self._on_instance_change)
        # 型ヒント
        self.view: NoteView

    def _on_instance_change(self) -> None:
        self.notes = []
        self.notes_point = 0
        self.view.textbox.value = NV_T.NOTE_NONE.value

    def recreate_before(self, view_: NoteView) -> None:
        self.view = view_
        self.theme = self.msk_.theme

    def recreate_after(self) -> None:
        self.view.textbox.value = self.txtbx_txt

    def on_change_txtbx(self) -> None:
        self.txtbx_txt = self.view.textbox.value

    def change_test(self) -> None:
        self.view.textbox.value += "\n".join(["", self.msk_.lang, str(self.msk_.valid_langs)])

    def quit_question(self) -> None:
        self.view.popup("Quit?", [NV_T.OK.value, NV_T.RETURN.value], self.quit)

    def quit(self, arg: int) -> None:
        if arg == 0:
            self.view.quit()
