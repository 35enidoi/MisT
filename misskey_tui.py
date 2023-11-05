from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.renderers import ImageFile
from asciimatics.widgets import Frame, Layout, TextBox, Button, PopUpDialog, VerticalDivider, Text
from asciimatics.exceptions import StopApplication, ResizeScreenError, NextScene
import requests
import io
from pyfiglet import figlet_format
from misskey import Misskey, exceptions
from random import randint
import sys

class MkAPIs():
    def __init__(self) -> None:
        # MisT settings
        self.theme = "default"
        self.cfgtxts = ""
        self.crnotetxts = "Tab to change widget"
        # Misskey py settings
        self.instance="misskey.io"
        self.i = None
        self.mk = None
        self.tl = "LTL"
        self.tl_len = 10
        self.nowpoint = 0
        self.notes = []
        self.reload()

    def reload(self):
        bef_mk = self.mk
        try:
            self.mk=Misskey(self.instance,self.i)
            if self.i is not None:
                self.mk.i()
            return True
        except (exceptions.MisskeyAPIException, requests.exceptions.ConnectionError):
            self.mk = bef_mk
            return False
    
    def get_i(self):
        try:
            return self.mk.i()
        except (exceptions.MisskeyAPIException, requests.exceptions.ConnectionError):
            return None

    def get_note(self):
        try:
            if self.tl == "HTL":
                self.notes = self.mk.notes_timeline(self.tl_len,with_files=False)
            elif self.tl == "LTL":
                self.notes = self.mk.notes_local_timeline(self.tl_len,with_files=False)
            elif self.tl == "STL":
                self.notes = self.mk.notes_hybrid_timeline(self.tl_len,with_files=False)
            elif self.tl == "GTL":
                self.notes = self.mk.notes_global_timeline(self.tl_len,with_files=False)
        except (exceptions.MisskeyAPIException, requests.exceptions.ReadTimeout):
            self.notes = []
    
    def note_update(self):
        noteid = self.notes[self.nowpoint]["id"]
        try:
            new_note = self.mk.notes_show(noteid)
            self.notes[self.nowpoint] = new_note
            return True
        except (exceptions.MisskeyAPIException, requests.exceptions.ReadTimeout):
            return False
    
    def get_instance_icon(self):
        try:
            iconurl = self.mk.meta()["iconUrl"]
            returns = requests.get(iconurl)
            if returns.status_code == 200:
                icon = io.BytesIO(returns.content)
                return icon
            else:
                raise exceptions.MisskeyAPIException
        except (exceptions.MisskeyAPIException, requests.exceptions.ConnectTimeout):
            return "Error"

    def create_note(self, text):
        try:
            return self.mk.notes_create(text)
        except exceptions.MisskeyAPIException:
            return None

class NoteView(Frame):
    def __init__(self, screen, msk):
        super(NoteView, self).__init__(screen,
                                       screen.height,
                                       screen.width,
                                       title="Notes",
                                       reduce_cpu=True,
                                       can_scroll=False)
        # initialize
        self.msk_ = msk
        self.set_theme(self.msk_.theme)

        # notebox create
        self.note=TextBox(screen.height-3,as_string=True,line_wrap=True)

        # button create
        buttonnames = ("Quit", "Move L", "Move R",
                       "Noteupdate", "Note Get", "More",
                       "Config")
        on_click = (self.pop_quit, self.move_l, self.move_r,
                    self.noteupdate, self.get_note, self.pop_more,
                    self.config)
        self.buttons = [Button(buttonnames[i], on_click[i]) for i in range(len(buttonnames))]

        # layout create
        layout = Layout([100])
        layout2 = Layout([1 for _ in range(len(self.buttons))])
        self.add_layout(layout)
        self.add_layout(layout2)

        # add widget
        layout.add_widget(self.note)
        for i in range(len(self.buttons)):
            layout2.add_widget(self.buttons[i],i)

        # define selfs
        self._move_l = self.buttons[1]
        self._move_r = self.buttons[2]
        self.layout = layout
        self.layout2 = layout2

        # disable
        self.note.disabled = True
        if self.msk_.i is None:
            self.buttons[-2].disabled = True
        else:
            self.buttons[-2].disabled = False
        if len(self.msk_.notes) == 0:
            self.buttons[3].disabled = True
        else:
            self.buttons[3].disabled = False

        # fix
        self._note_reload()
        self.fix()

    def get_note(self):
        self.msk_.get_note()
        self.msk_.nowpoint=0
        self._note_reload()
    
    def noteupdate(self):
        is_ok = self.msk_.note_update()
        if is_ok:
            self._note_reload()
        else:
            self._scene.add_effect(PopUpDialog(self.screen,"something occured", ["ok"]))

    def move_r(self):
        self.msk_.nowpoint += 1
        self._note_reload()

    def move_l(self):
        self.msk_.nowpoint -= 1
        self._note_reload()

    def _note_reload(self):
        self.note.value = f"<{self.msk_.nowpoint+1}/{len(self.msk_.notes)}>\n"
        if len(self.msk_.notes) == 0:
            self._noteput("something occured while noteget.","or welcome to MisT!")
            self.buttons[3].disabled = True
        else:
            self.buttons[3].disabled = False
            self._note_inp(self.msk_.notes[self.msk_.nowpoint])
            if self.msk_.notes[self.msk_.nowpoint].get("renote"):
                self._note_inp(self.msk_.notes[self.msk_.nowpoint]["renote"])
        if self.msk_.nowpoint == 0:
            self._move_l.disabled = True
            self.switch_focus(self.layout2,2,0)
        else:
            self._move_l.disabled = False
        if (self.msk_.nowpoint == len(self.msk_.notes)-1) or (self.msk_.nowpoint == len(self.msk_.notes)):
            self._move_r.disabled = True
            self.switch_focus(self.layout2,1,0)
        else:
            self._move_r.disabled = False

    def _note_inp(self,note):
        if note["user"]["host"] is None:
            username = f'@{note["user"]["username"]}@{self.msk_.instance}'
        else:
            username = f'@{note["user"]["username"]}@{note["user"]["host"]}'
        if note["user"]["name"] is None:
            name = note["user"]["username"]
        else:
            name = note["user"]["name"]
        if note["renoteId"] is not None:
            self._noteput(f"{name} [{username}] was renoted    noteId:{note['id']}", "-"*(self.screen.width-8))
        else:
            self._noteput(f"{name} [{username}] was noted    noteId:{note['id']}", "-"*(self.screen.width-8))
        if note["cw"] is not None:
            self._noteput("CW detect!","~"*(self.screen.width-8),note["cw"])
        self._noteput(note["text"],"")
        if len(note["files"]) != 0:
            self._noteput(f'{len(note["files"])} files')
        self._noteput(f'{note["renoteCount"]} renotes {note["repliesCount"]} replys {sum(note["reactions"].values())} reactions',
                        "  ".join(f'{i.replace("@.","")}[{note["reactions"][i]}]' for i in note["reactions"].keys()))

    def _noteput(self,*arg):
        for i in arg:
            self.note.value += str(i)+"\n"

    def pop_more(self):
        self._scene.add_effect(PopUpDialog(self.screen,"?", ["Create Note", "Renote", "Reaction", "return"],on_close=self._ser_more))

    def pop_quit(self):
        self._scene.add_effect(PopUpDialog(self.screen,"Quit?", ["yes", "no"],on_close=self._ser_quit))

    def _ser_more(self,arg):
        if arg == 0:
            raise NextScene("CreateNote")
        elif arg == 1:
            self._scene.add_effect(PopUpDialog(self.screen,"this is not working :(", ["Ok"]))
        elif arg == 2:
            self._scene.add_effect(PopUpDialog(self.screen,"this is not working :(", ["Ok"]))

    @staticmethod
    def _ser_quit(arg):
        if arg == 0:
            raise StopApplication("UserQuit")

    @staticmethod
    def config():
        raise NextScene("Configration")

class ConfigMenu(Frame):
    def __init__(self, screen, msk):
        super(ConfigMenu, self).__init__(screen,
                                       screen.height,
                                       screen.width,
                                       title="ConfigMenu",
                                       reduce_cpu=True,
                                       can_scroll=False)
        # initialize
        self.msk_ = msk
        self._ok_value = ""

        # txts create
        self.txtbx = TextBox(screen.height-1,as_string=True,line_wrap=True)
        self.txt = Text()
        self.txtbx.value = self.msk_.cfgtxts

        # buttons create
        buttonnames = ("Return", "Change TL", "Change Theme",
                       "TOKEN", "Instance", "Version", "Clear",
                       "Refresh", "OK")
        onclicks = (self.return_, self.poptl, self.poptheme,
                    self.poptoken, self.instance_, self.version_, self.clear_,
                    self.refresh_,self.ok_)
        self.buttons = [Button(buttonnames[i],onclicks[i]) for i in range(len(buttonnames))]

        # Layout create
        self.set_theme(self.msk_.theme)
        layout = Layout([screen.width,2,20])
        self.add_layout(layout)
        self.layout = layout

        # add widget
        layout.add_widget(self.txtbx,0)
        layout.add_widget(VerticalDivider(screen.height),1)
        for i in self.buttons:
            layout.add_widget(i,2)
        layout.add_widget(self.txt,2)

        # disables
        self.txtbx.disabled = True
        self.txt.disabled = True
        self.buttons[-1].disabled = True

        # fix
        self.fix()

    def version_(self):
        fonts = ["binary","chunky","contessa","cybermedium","hex","eftifont","italic","mini","morse","short"]
        randomint = randint(0,len(fonts)+1)
        if randomint == len(fonts):
            mist_figs = "MisT\n"
        elif randomint == len(fonts)+1:
            mist_figs = """
MM     MM     TTTTTTTTTTT
M M   M M  I       T
M  M M  M  I  SSS  T
M   M   M     S    T
M       M  I  SSS  T
M       M  I    S  T
M       M  I  SSS  T """
        else:
            mist_figs = figlet_format("MisT",fonts[randomint])
        version = "v0.1.0"
        self._txtbxput(mist_figs+version,"","write by 35enidoi","@iodine53@misskey.io","")

    def clear_(self):
        self.txtbx.value = ""
        self.msk_.cfgtxts = ""

    def _txtbxput(self,*arg):
        for i in arg:
            self.txtbx.value += str(i)+"\n"
        self.msk_.cfgtxts = self.txtbx.value

    def poptl(self):
        self._scene.add_effect(PopUpDialog(self.screen,"Change TL", ["HTL", "LTL", "STL", "GTL"],on_close=self._ser_tl))

    def poptheme(self):
        self._scene.add_effect(PopUpDialog(self.screen,"Change Theme", ["default", "monochrome", "green", "bright", "return"],on_close=self._ser_theme))

    def poptoken(self):
        self._scene.add_effect(PopUpDialog(self.screen,"How to?", ["MiAuth", "TOKEN", "return"],self._ser_token))

    def _ser_tl(self,arg):
        if arg == 0:
            if self.msk_.i is not None:
                self.msk_.tl = "HTL"
                self._txtbxput("change TL:HomeTL")
            else:
                self._txtbxput("HTL is TOKEN required")
        elif arg == 1:
            self.msk_.tl = "LTL"
            self._txtbxput("change TL:LocalTL")
        elif arg == 2:
            if self.msk_.i is not None:
                self.msk_.tl = "STL"
                self._txtbxput("change TL:SocialTL")
            else:
                self._txtbxput("STL is TOKEN required")
        elif arg == 3:
            self.msk_.tl = "GTL"
            self._txtbxput("change TL:GlobalTL")

    def _ser_theme(self,arg):
        if arg == 0:
            self.msk_.theme = "default"
        elif arg == 1:
            self.msk_.theme = "monochrome"
        elif arg == 2:
            self.msk_.theme = "green"
        elif arg == 3:
            self.msk_.theme = "bright"
        elif arg == 4:
            return
        raise ResizeScreenError("self error")

    def _ser_token(self,arg):
        if arg == 0:
            self._txtbxput("this is not working sorry :(")
        elif arg == 1:
            self._ok_value="TOKEN"
            self.txt.disabled = False
            for i in self.buttons:
                i.disabled = True
            self.buttons[-1].disabled = False
            self.switch_focus(self.layout,2,len(self.buttons))

    def instance_(self):
        self._ok_value = "INSTANCE"
        self._txtbxput("input instance such as 'misskey.io' 'misskey.backspace.fm'", f"current instance:{self.msk_.instance}","")
        self.txt.disabled = False
        for i in self.buttons:
            i.disabled = True
        self.buttons[-1].disabled = False
        self.switch_focus(self.layout,2,len(self.buttons))

    def ok_(self):
        if self._ok_value == "TOKEN":
            self.msk_.i = self.txt.value
            is_ok = self.msk_.reload()
            if is_ok:
                self._txtbxput("TOKEN check OK :)")
                i = self.msk_.get_i()
                if i is None:
                    self._txtbxput("fail to get your info :(")
                else:
                    self._txtbxput(f"Hello {i['name']}!")
            else:
                self._txtbxput("TOKEN check fail :(")
        elif self._ok_value == "INSTANCE":
            before_instance = self.msk_.instance
            self.msk_.instance = self.txt.value
            is_ok = self.msk_.reload()
            if is_ok:
                self._txtbxput("instance connected! :)")
                icon_bytes = self.msk_.get_instance_icon()
                if icon_bytes == "Error":
                    self._txtbxput("error occured while get icon :(")
                else:
                    icon = ImageFile(icon_bytes,self.screen.height//2)
                    self._txtbxput(icon)
            else:
                self.msk_.instance = before_instance
                self._txtbxput("instance connect fail :(")
            self._txtbxput(f"current instance:{self.msk_.instance}","")
        self._ok_value = ""
        self.txt.value = ""
        self.txt.disabled = True
        for i in self.buttons:
            i.disabled = False
        self.buttons[-1].disabled = True
        self.switch_focus(self.layout,2,0)

    def refresh_(self):
        raise ResizeScreenError("self error", self._scene)

    @staticmethod
    def return_():
        raise NextScene("Main")

class CreateNote(Frame):
    def __init__(self, screen, msk):
        super(CreateNote, self).__init__(screen,
                                      screen.height,
                                      screen.width,
                                      title="CreateNote",
                                      reduce_cpu=True,
                                      can_scroll=False)
        # initialize
        self.msk_ = msk
        self.set_theme(self.msk_.theme)

        # txtbox create
        self.txtbx = TextBox(screen.height-3, as_string=True, line_wrap=True,on_change=self.reminder)
        self.txtbx.value = self.msk_.crnotetxts

        # buttons create
        buttonnames = ("Note Create", "return")
        on_click = (self.popcreatenote, self.return_)
        self.buttons = [Button(buttonnames[i],on_click[i]) for i in range(len(buttonnames))]

        # Layout create
        layout = Layout([100])
        layout2 = Layout([1 for _ in range(len(self.buttons))])
        self.add_layout(layout)
        self.add_layout(layout2)

        # add widget
        layout.add_widget(self.txtbx)
        for i in range(len(self.buttons)):
            layout2.add_widget(self.buttons[i],i)

        # fix
        self.fix()

    def reminder(self):
        self.msk_.crnotetxts = self.txtbx.value

    def popcreatenote(self):
        self._scene.add_effect(PopUpDialog(self.screen,"Are you sure about that?", ["Sure", "No"],self._ser_createnote))

    def _ser_createnote(self,arg):
        if arg == 0:
            return_ = self.msk_.create_note(self.txtbx.value)
            if return_ is not None:
                self._scene.add_effect(PopUpDialog(self.screen,"Create note success :(", ["Ok"]))
            else:
                self._scene.add_effect(PopUpDialog(self.screen,"Create note fail :(", ["Ok"]))

    @staticmethod
    def return_():
        raise NextScene("Main")

def wrap(screen, scene):
    scenes = [Scene([NoteView(screen, msk)], -1, name="Main"),
              Scene([ConfigMenu(screen, msk)], -1, name="Configration"),
              Scene([CreateNote(screen,msk)], -1, name="CreateNote")]
    screen.play(scenes, stop_on_resize=True, start_scene=scene, allow_int=True)

msk = MkAPIs()
last_scene = None
while True:
    try:
        Screen.wrapper(wrap, catch_interrupt=True, arguments=[last_scene])
        sys.exit(0)
    except ResizeScreenError as e:
        last_scene = e.scene