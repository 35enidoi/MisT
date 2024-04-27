from misskey_tui.model import MkAPIs
from misskey_tui.scenes.noteview.view import NoteView
from misskey_tui.textenums import NV_T


class NoteViewModel:
    """NoteViewのViewModel"""
    def __init__(self, msk: MkAPIs) -> None:
        # modelの保存
        self.msk_ = msk
        # 変数作成
        self.txtbx_txt: str = "Hello World!\nWelcome to MisT with MVVM model!"
        self.notes = []
        self.notes_point = []
        self.TL = "HTL"
        self.theme = self.msk_.theme
        self.button_names = (NV_T.QUIT.value, "Change")
        self.button_funcs = (self.quit_question, self.change_test)
        # 型ヒント
        self.view: NoteView

    def recreate_before(self, view_: NoteView) -> None:
        self.view = view_
        self.theme = self.msk_.theme

    def recreate_after(self) -> None:
        self.txtbx_write()

    def change_test(self) -> None:
        self.txtbx_txt += "\nHoni"
        self.txtbx_write()

    def txtbx_write(self) -> None:
        self.view.textbox.value = self.txtbx_txt

    def quit_question(self) -> None:
        self.view.popup("Quit?", [NV_T.OK.value, NV_T.RETURN.value], self.quit)

    def quit(self, arg: int) -> None:
        if arg == 0:
            self.view.quit()
