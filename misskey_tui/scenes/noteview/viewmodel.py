from typing import Callable, Any, Literal, TYPE_CHECKING

from misskey_tui.model import MkAPIs
from misskey_tui.textenums import NV_T
from misskey_tui.abstract import AbstractViewModel
from misskey_tui.enum.misskeypy_return import Note
from misskey_tui.util import nyaize

if TYPE_CHECKING:
    from misskey_tui.scenes.noteview.view import NoteView


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
        self.view: "NoteView"

    def _on_instance_change(self) -> None:
        self.notes = []
        self.notes_point = 0
        self.view.textbox.value = NV_T.NOTE_NONE.value

    def recreate_before(self, view_: "NoteView") -> None:
        self.view = view_
        self.theme = self.msk_.theme

    def recreate_after(self) -> None:
        self.view.textbox.value = self.txtbx_txt

    def on_change_txtbx(self) -> None:
        self.txtbx_txt = self.view.textbox.value  # type: ignore  textbox.valueは必ずstr

    def note_get_func(self) -> Callable[[Any], list[Note]]:
        if self.TL == "HTL":
            return self.msk_.mk.notes_timeline  # type: ignore  list[Note]が返ってくる
        elif self.TL == "LTL":
            return self.msk_.mk.notes_local_timeline  # type: ignore  同文
        elif self.TL == "STL":
            return self.msk_.mk.notes_hybrid_timeline  # type: ignore  同文
        elif self.TL == "GTL":
            return self.msk_.mk.notes_global_timeline  # type: ignore  同文
        else:
            raise ValueError(f"Unknown TL type: {self.TL}")

    def note_get(self) -> None:
        if self.msk_.is_valid_misskeypy:
            notes = self.msk_.misskeypy_wrapper(self.note_get_func(), limit=10)
            if notes is not None:
                # get success
                self.notes = notes
                self.notes_point = 0  # 新規取得時は先頭にリセット
                self.view.popup(NV_T.GET_NOTE_SUCCESS.value, [NV_T.OK.value])
            else:
                # get fail
                additional_text = ""
                if self.msk_.now_user_info is None:
                    additional_text = NV_T.GET_NOTE_FAIL_ADDITIONAL_1._value_
                    if self.TL in ("HTL", "STL"):
                        additional_text = NV_T.GET_NOTE_FAIL_ADDITIONAL_2.value + f"; {self.TL}"
                self.view.popup(NV_T.GET_NOTE_FAIL.value + "\n" + additional_text, [NV_T.OK.value])
        else:
            self.view.popup(NV_T.GET_NOTE_MISSKEYPY_INVALID.value, [NV_T.OK.value])

        self.note_write()

    # --- 追加: ノート移動関数 ---
    def next_note(self) -> None:
        """次のノートへ移動 (末尾を超えない)."""
        if not self.notes:
            return
        if self.notes_point < len(self.notes) - 1:
            self.notes_point += 1
            self.note_write()

    def prev_note(self) -> None:
        """前のノートへ移動 (0未満にならない)."""
        if not self.notes:
            return
        if self.notes_point > 0:
            self.notes_point -= 1
            self.note_write()

    def note_write(self) -> None:
        self.view.textbox.value = ""  # 初期化

        if self.notes != []:
            # ノートがある時
            return_strs = []

            return_strs.append(f"<{self.notes_point + 1}/{len(self.notes)}>\n")

            return_strs.append(self._note_inp(self.notes[self.notes_point]))
            if (renote := self.notes[self.notes_point].get("renote")):
                return_strs.append(self._note_inp(renote))

            self.view.textbox.value = "\n".join(return_strs)
        else:
            # ノート無い時
            self.view.textbox.value = NV_T.NOTE_NONE.value

    def _note_inp(self, note: Note) -> str:
        return_strs = []

        # usernameの取得
        if note["user"]["host"] is None:
            username = f'@{note["user"]["username"]}@{self.msk_.instance}'
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
