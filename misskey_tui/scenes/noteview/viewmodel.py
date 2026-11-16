from typing import TYPE_CHECKING

from misskey_tui.enum.timeline import Timeline
from misskey_tui.model.model import Model
from misskey_tui.textenums import NV_T
from misskey_tui.abstract import AbstractViewModel
from misskey_tui.enum.misskeypy_return import Note
from misskey_tui.model.events import timeline_hundler, config_user_hundler
from misskey_tui.enum.events import (
    ConfigUserEvent, ConfigThemeChangeEventMessage,
    TimelineRefreshSuccessEvent, TimelineIndexChangeEvent, TimelineErrorChangeEvent,
    TimelineTLChangeEvent, TimelineClearEvent, TimelineEvent
)
from misskey_tui.util import nyaize

if TYPE_CHECKING:
    from misskey_tui.scenes.noteview.view import NoteView


class NoteViewModel(AbstractViewModel):
    """NoteViewのViewModel"""
    def __init__(self, model: Model) -> None:
        # modelの保存
        self.model = model
        # 変数作成
        self.txtbx_txt: str = NV_T.WELCOME_MESSAGE.value
        self.theme = self.model.config.theme
        # フック作成
        self.model.mkapi.add_on_change_instance(self._on_instance_change)
        timeline_hundler.add_handler(self._on_timeline_event)
        # 型ヒント
        self.view: "NoteView"

    def _on_instance_change(self) -> None:
        self.notes = []
        self.notes_point = 0
        self.view.textbox.value = NV_T.NOTE_NONE.value
        self.update_nav_buttons()

    def _on_timeline_event(self, event: TimelineEvent) -> None:
        match event:
            case TimelineRefreshSuccessEvent():
                self.note_write()
            case TimelineIndexChangeEvent():
                self.note_write()
            case TimelineTLChangeEvent():
                self.note_write()
            case TimelineClearEvent():
                self.note_write()
            case TimelineErrorChangeEvent():
                message = "something was occured: " + event.reason
                if event.detail is not None:
                    message += f"\n(detail: {event.detail})"
                self.view.popup(message, [NV_T.OK.value], lambda _: None)
            case _:
                print("Unknown timeline event:", event)  # debug
                pass

    def _on_config_event(self, event: ConfigUserEvent):
        match event:
            case ConfigThemeChangeEventMessage():
                self.theme = event.theme

    def recreate_before(self, view_: "NoteView") -> None:
        self.view = view_
        self.theme = self.model.config.theme

    def recreate_after(self) -> None:
        self.view.textbox.value = self.txtbx_txt
        self.update_nav_buttons()

    def on_change_txtbx(self) -> None:
        value = self.view.textbox.value
        if isinstance(value, list):
            self.txtbx_txt = "\n".join(str(v) for v in value)
        else:
            self.txtbx_txt = str(value)

    def button_tl_change(self) -> None:
        def on_select(arg: int) -> None:
            tl_types = [i for i in Timeline]
            if 0 <= arg < len(tl_types):
                self.model.timeline_service.set_tl(tl_types[arg])
                self.model.timeline_service.refresh()
            else:
                # return
                pass

        self.view.popup("Select a timeline:", [i for i in Timeline] + ["return"], on_select)

    def note_get(self) -> None:
        self.model.timeline_service.refresh()

    def next_note(self) -> None:
        """次のノートへ移動"""
        try:
            self.model.timeline_service.index += 1
        except IndexError:
            pass

        self.update_nav_buttons()
        self.note_write()

    def prev_note(self) -> None:
        """前のノートへ移動"""
        try:
            self.model.timeline_service.index -= 1
        except IndexError:
            pass

        self.update_nav_buttons()
        self.note_write()

    def update_nav_buttons(self) -> None:
        """Prev/Nextボタンの有効無効を更新"""
        if not self.model.timeline_service.notes:
            self.view.set_nav_enabled(False, False)
        else:
            prev_en = self.model.timeline_service.index > 0
            next_en = self.model.timeline_service.index < len(self.model.timeline_service.notes) - 1

            self.view.set_nav_enabled(prev_en, next_en)

    def note_write(self) -> None:
        self.view.textbox.value = ""  # 初期化

        if self.model.timeline_service.notes:
            # ノートがある時
            return_strs = []

            return_strs.append(f"<{self.model.timeline_service.index + 1}/{len(self.model.timeline_service.notes)}>\n")

            return_strs.append(self._note_inp(self.model.timeline_service.notes[self.model.timeline_service.index]))
            if (renote := self.model.timeline_service.notes[self.model.timeline_service.index].get("renote")):
                return_strs.append(self._note_inp(renote))

            self.view.textbox.value = "\n".join(return_strs)
        else:
            # ノート無い時
            self.view.textbox.value = NV_T.NOTE_NONE.value

        self.update_nav_buttons()

    def _note_inp(self, note: Note) -> str:
        return_strs = []

        # usernameの取得
        if note["user"]["host"] is None:
            username = f'@{note["user"]["username"]}@{self.model.mkapi.instance}'
        else:
            username = f'@{note["user"]["username"]}@{note["user"]["host"]}'

        # ユーザー名の取得
        if note["user"]["name"] is None:
            name = note["user"]["username"]
        else:
            name = note["user"]["name"]

        # どのようなノートなのか確認
        if note["replyId"] is not None:
            # 返信
            return_strs.append(f"{name} [{username}] was replied    noteId:{note['id']}")
        elif note["renoteId"] is not None:
            if note["text"] is not None:
                # 引用
                return_strs.append(f"{name} [{username}] was quoted     noteId:{note['id']} text:{note['text']}")
            else:
                # リノート
                return_strs.append(f"{name} [{username}] was renoted    noteId:{note['id']}")
        else:
            # 通常のノート
            return_strs.append(f"{name} [{username}] was noted      noteId:{note['id']}")

        # ユーザーの特殊フラグを取得
        flags = []

        if note["user"]["isBot"]:
            flags.append("isBot:True")
        if note["user"]["isCat"]:
            flags.append("isCat:True")

        if flags:
            return_strs.append(" ".join(flags))

        # ユーザーのroleを取得
        if (badge_roles := note["user"].get("badgeRoles")):
            if len(badge_roles) != 0:
                return_strs.append("badgeRoles:["+",".join(i["name"] for i in badge_roles)+"]")

        # 区切り線
        return_strs.append("-"*(self.view.screen.width-4))

        # Todo: これなに
        if note["text"] is None:
            if len(note["files"]) == 0:
                return "\n".join(return_strs)

        # CWがあればそれを先に記載
        if note["cw"] is not None:
            return_strs.append("CW detect!")
            return_strs.append(note["cw"])
            return_strs.append("~"*(self.view.screen.width-4))

        # テキストの処理
        if note["user"]["isCat"]:
            return_strs.append(nyaize(str(note["text"])))
        else:
            return_strs.append(note["text"])

        # 一行開ける
        return_strs.append("")

        # 添付ファイルの処理
        if len(note["files"]) != 0:
            return_strs.append("{} files".format(len(note["files"])))

        # ノートのリノートや返信の情報を取得
        renote_count = note.get("renoteCount", 0)
        replies_count = note.get("repliesCount", 0)
        reactions = note.get("reactions", {})

        return_strs.append(f'{renote_count} renotes {replies_count} replys {sum(reactions.values())} reactions')

        # リアクション情報を書き込み
        return_strs.append("  ".join(f'{i.replace("@.", "")}[{reactions[i]}]' for i in reactions.keys()))

        # 改行
        return_strs.append("")

        return "\n".join(return_strs)

    def quit_question(self) -> None:
        self.view.popup(NV_T.QUIT.value, [NV_T.OK.value, NV_T.RETURN.value], self.quit)

    def quit(self, arg: int) -> None:
        if arg == 0:
            self.view.quit()
