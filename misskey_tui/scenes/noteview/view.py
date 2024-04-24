from asciimatics.widgets import Frame, Layout, TextBox, PopUpDialog, Button
from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.exceptions import StopApplication

from misskey_tui.textenums import NV_T

class NoteView(Frame):
    def __init__(self, screen:Screen, mv):
        super(NoteView, self).__init__(screen,
                                 screen.height,
                                 screen.width,
                                 title="NoteView",
                                 on_load=None,
                                 reduce_cpu=True,
                                 can_scroll=False)
        # MVの保存
        self.mv_ = mv
        # 初期化
        self.mv_.recreate_before(self)
        self.set_theme(self.mv_.theme)
        # 型推測付与
        self.screen:Screen
        self._scene:Scene

        # textboxの作成
        self.textbox = TextBox(screen.height-3, as_string=True, line_wrap=True, readonly=True)

        # buttonの作成
        buttonnames = (NV_T.BT_QUIT.value, "change text")
        on_click = (self.quit, self.mv_.change_test)
        self.buttons = tuple(Button(text=name, on_click=func) for name, func in zip(buttonnames, on_click))

        # layoutの作成
        layout0 = Layout([100])
        layout1 = Layout([1 for _ in range(len(self.buttons))])
        self.add_layout(layout0)
        self.add_layout(layout1)

        # layoutにウィジェットを追加
        layout0.add_widget(self.textbox)
        for ind, val in enumerate(self.buttons):
            layout1.add_widget(val, ind)
        
        # 後処理
        self.fix()
        self.mv_.recreate_after()

    def pop_quit(self, arg=-1):
        if arg == -1:
            # init
            self.popup(NV_T.QUIT.value, [NV_T.RETURN.value, NV_T.OK.value], self.pop_quit)
        elif arg == 1:
            #quit
            self.quit()

    def popup(self,txt,button,on_close=None):
        self._scene.add_effect(PopUpDialog(self.screen, txt, button, on_close))

    @staticmethod
    def quit():
        raise StopApplication("honi")