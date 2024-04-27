from asciimatics.widgets import Frame, Layout, TextBox, Button, VerticalDivider
from asciimatics.screen import Screen
from asciimatics.scene import Scene


class ConfigMenuView(Frame):
    def __init__(self,
                 screen: Screen,
                 mv) -> None:
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
        self.txtbx = TextBox(self.screen.height-2, as_string=True, readonly=True, line_wrap=True)
        self.txtbx.disabled = True

        # buttonの作成
        self.buttons = tuple(Button(text=name, on_click=func) for name, func in zip(self.mv_.button_names,
                                                                                    self.mv_.button_funcs))

        # layoutの作成
        layout0 = Layout([max(map(len, self.mv_.button_names))*2, 1, 100-max(map(len, self.mv_.button_names))*2-1])
        self.add_layout(layout0)

        # layoutにウィジェットを追加
        for i in self.buttons:
            layout0.add_widget(i, column=0)
        layout0.add_widget(VerticalDivider(self.screen.height), column=1)
        layout0.add_widget(self.txtbx, column=2)

        # 後処理
        self.fix()
        self.mv_.recreate_after()
