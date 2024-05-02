from typing import Callable, Optional, NoReturn

from asciimatics.widgets import Frame, Layout, TextBox, PopUpDialog, Button, Divider
from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.exceptions import StopApplication

from misskey_tui.abstract.viewmodel import AbstractViewModel


class NoteView(Frame):
    def __init__(self,
                 screen: Screen,
                 mv: AbstractViewModel) -> None:
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
        self.screen: Screen
        self._scene: Scene

        # textboxの作成
        self.textbox = TextBox(screen.height-4, as_string=True,
                               line_wrap=True, readonly=True,
                               on_change=self.mv_.on_change_txtbx)

        # buttonの作成
        self.buttons = tuple(Button(text=name, on_click=func) for name, func in zip(self.mv_.button_names,
                                                                                    self.mv_.button_funcs))

        # layoutの作成
        layout0 = Layout([100])
        layout1 = Layout([1])
        layout2 = Layout([1 for _ in range(len(self.buttons))])
        self.add_layout(layout0)
        self.add_layout(layout1)
        self.add_layout(layout2)

        # layoutにウィジェットを追加
        layout0.add_widget(self.textbox)
        layout1.add_widget(Divider())
        for ind, val in enumerate(self.buttons):
            layout2.add_widget(val, ind)

        # 後処理
        self.fix()
        self.mv_.recreate_after()

    def popup(self,
              txt: str,
              button: list[str],
              on_close: Optional[Callable[[int], None]] = None) -> None:
        self._scene.add_effect(PopUpDialog(self.screen, txt, button, on_close))

    @staticmethod
    def quit() -> NoReturn:
        raise StopApplication("nyaaan")
