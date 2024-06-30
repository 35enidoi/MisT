from typing import Callable, Any, Literal

from misskey_tui.model import MkAPIs
from misskey_tui.scenes.noteview.view import NoteView
from misskey_tui.textenums import NV_T
from misskey_tui.abstract import AbstractViewModel
from misskey_tui.enum.misskeypy_return import Note


class NoteViewModel(AbstractViewModel):
    """NoteViewのViewModel"""
    def __init__(self, msk: MkAPIs) -> None:
        # modelの保存
        self.msk_ = msk
        # 変数作成
        self.txtbx_txt: str = NV_T.WELCOME_MESSAGE.value
        self.notes: list[Note] = []
        self.notes_point: int = 0
        self.TL: Literal["HTL", "LTL", "STL", "GTL"] = "LTL"
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

    def note_get_func(self) -> Callable[[Any], Note]:
        if self.TL == "HTL":
            return self.msk_.mk.notes_timeline
        elif self.TL == "LTL":
            return self.msk_.mk.notes_local_timeline
        elif self.TL == "STL":
            return self.msk_.mk.notes_hybrid_timeline
        elif self.TL == "GTL":
            return self.msk_.mk.notes_global_timeline

    def note_get(self) -> None:
        if self.msk_.is_valid_misskeypy:
            notes = self.msk_.misskeypy_wrapper(self.note_get_func(), limit=10)
            if notes is not None:
                # get success
                self.notes = notes
                self.view.popup("get note success!", ["Ok"])
            else:
                # get fail
                additional_text = ""
                if self.msk_.now_user_info is None:
                    additional_text = "Maybe cause no token."
                    if self.TL in ("HTL", "STL"):
                        additional_text = f"Maybe cause select invalid TL;{self.TL}"
                self.view.popup("Something was occured while get note.\n" + additional_text,
                                ["Ok"])
        else:
            self.view.popup("misskeypy is invalid. reconnect instance please", ["ok"])

    def change_test(self) -> None:
        self.view.textbox.value += "\n".join(["", self.msk_.lang, str(self.msk_.valid_langs)])

    def quit_question(self) -> None:
        self.view.popup("Quit?", [NV_T.OK.value, NV_T.RETURN.value], self.quit)

    def quit(self, arg: int) -> None:
        if arg == 0:
            self.view.quit()
