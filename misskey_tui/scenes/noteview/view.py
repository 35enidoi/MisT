from asciimatics.widgets import Frame, TextBox
from asciimatics.screen import Screen
from noteview.viewmodel import NV_VM

class NoteView(Frame):
    def __init__(self, screen:Screen, mv:NV_VM):
        super(NoteView).__init__(screen,
                                 screen.height,
                                 screen.width,
                                 title="NoteView",
                                 on_load=None,
                                 reduce_cpu=True,
                                 can_scroll=False)
        # MVの保存
        self.mv_ = mv
        # screenに型推測付与
        self.screen:Screen