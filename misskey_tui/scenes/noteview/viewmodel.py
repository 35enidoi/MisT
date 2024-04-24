from misskey_tui.model import MkAPIs

class NV_VM:
    """NoteViewのViewModel"""
    def __init__(self, msk:MkAPIs) -> None:
        # modelの保存
        self.msk_ = msk
        # 変数作成
        self.txtbx_txt = "Hello World!\nWelcome to MisT with MVVM model!"
        self.notes = []
        self.notes_point = []
        self.TL = "HTL"
