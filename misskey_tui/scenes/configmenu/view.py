from typing import Optional, Callable, NoReturn
from functools import partial

from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.exceptions import NextScene
from asciimatics.widgets import (Frame,
                                 Layout,
                                 TextBox,
                                 Button,
                                 VerticalDivider,
                                 Text,
                                 Divider,
                                 PopUpDialog)

from misskey_tui.abstract.viewmodel import AbstractViewModel
from misskey_tui.textenums import CM_T
from misskey_tui.util import check_terminal_haba


class ConfigMenuView(Frame):
    def __init__(self,
                 screen: Screen,
                 mv: AbstractViewModel) -> None:
        super(ConfigMenuView, self).__init__(screen,
                                             screen.height,
                                             screen.width,
                                             title="ConfigMenu",
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

        # txtbxの作成
        self.txtbx = TextBox(self.screen.height-2, as_string=True,
                             readonly=True, line_wrap=True,
                             on_change=self.mv_.on_change_txtbx)
        self.txtbx.disabled = True
        self.inp_bx = Text(on_change=self.mv_.on_change_inpbx)

        # buttonの作成
        button_names = (CM_T.RETURN.value, CM_T.TOKEN_BUTTON.value, CM_T.INSTANCE_BUTTON.value,
                        CM_T.THEME_BUTTON.value, CM_T.LANGUAGE_BUTTON.value, CM_T.CLEAR_BUTTON.value)
        button_funcs = (partial(self.change_window, "NoteView"), self.mv_.token, self.mv_.instance,
                        self.mv_.theme_, self.mv_.language, self.mv_.clear_text)

        self.buttons = tuple(Button(text=name, on_click=func) for name, func in zip(button_names,
                                                                                    button_funcs))
        self.ok_button = Button(*self.mv_.ok_button)
        max_button_length = max(map(check_terminal_haba, button_names))

        # layoutの作成
        layout0 = Layout([max_button_length, 1, 100-max_button_length-1])
        self.layout = layout0
        self.add_layout(layout0)

        # layoutにウィジェットを追加
        for i in self.buttons:
            layout0.add_widget(i, column=0)
        layout0.add_widget(Divider(), column=0)
        layout0.add_widget(self.ok_button, column=0)
        layout0.add_widget(self.inp_bx, column=0)
        layout0.add_widget(VerticalDivider(self.screen.height), column=1)
        layout0.add_widget(self.txtbx, column=2)

        # 後処理
        self.fix()
        self.mv_.recreate_after()

    def popup(self,
              txt: str,
              button: list[str],
              on_close: Optional[Callable[[int], None]] = None) -> None:
        self._scene.add_effect(PopUpDialog(self.screen, txt, button, on_close))

    @staticmethod
    def change_window(target_name: str) -> NoReturn:
        raise NextScene(target_name)
