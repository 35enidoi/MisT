from asciimatics.scene import Scene
from asciimatics.widgets import Frame, Layout, TextBox, Button, PopUpDialog, VerticalDivider, RadioButtons
from asciimatics.screen import Screen
from asciimatics.exceptions import StopApplication, ResizeScreenError, NextScene
from pyfiglet import figlet_format
from misskey import Misskey, exceptions
from random import randint
import sys

class MkAPIs():
    def __init__(self) -> None:
        # MisT settings
        self.theme = "default"
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
            return True
        except exceptions.MisskeyAPIException as e:
            self.mk = bef_mk
            return False

    def get_note(self):
        try:
            if self.tl == "HTL":
                self.notes = self.mk.notes_timeline(self.tl_len)
            elif self.tl == "LTL":
                self.notes = self.mk.notes_local_timeline(self.tl_len)
            elif self.tl == "STL":
                self.notes = self.mk.notes_hybrid_timeline(self.tl_len)
            elif self.tl == "GTL":
                self.notes = self.mk.notes_global_timeline(self.tl_len)
        except exceptions.MisskeyAPIException:
            self.notes = []

class NoteView(Frame):
    def __init__(self, screen, msk):
        super(NoteView, self).__init__(screen,
                                       screen.height,
                                       screen.width,
                                       title="Notes",
                                       reduce_cpu=True,
                                       can_scroll=False)
        self.msk_ = msk
        self.set_theme(self.msk_.theme)
        layout = Layout([1,98,1])
        layout2 = Layout([1,1,1,1,1])
        self.note=TextBox(screen.height-3,as_string=True,line_wrap=True)
        self._move_r = Button("Move R",self.move_r,name="move r")
        self._move_l = Button("Move L",self.move_l,name="move l")
        self.note.disabled = True
        self.add_layout(layout)
        self.add_layout(layout2)
        layout.add_widget(self.note,1)
        layout2.add_widget(Button("Quit",self._quit),0)
        layout2.add_widget(self._move_l,1)
        layout2.add_widget(self._move_r,2)
        layout2.add_widget(Button("Note Get",self.get_note),3)
        layout2.add_widget(Button("Config",self.config),4)
        self.layout = layout
        self.layout2 = layout2
        self._note_reload()
        self.fix()

    def get_note(self):
        self.msk_.get_note()
        self.msk_.nowpoint=0
        self._note_reload()

    def move_r(self):
        self.msk_.nowpoint += 1
        self._note_reload()

    def move_l(self):
        self.msk_.nowpoint -= 1
        self._note_reload()

    def _note_reload(self):
        self.note.value = f"<{self.msk_.nowpoint+1}/{len(self.msk_.notes)}>\n"
        if len(self.msk_.notes) == 0:
            self._noteput("something occured while noteget or welcome to MisT!")
        else:
            noteval = self.msk_.notes[self.msk_.nowpoint]
            if noteval["user"]["host"] is None:
                username = f'@{noteval["user"]["username"]}@{self.msk_.instance}'
            else:
                username = f'@{noteval["user"]["username"]}@{noteval["user"]["host"]}'
            if noteval["user"]["name"] is None:
                name = noteval["user"]["username"]
            else:
                name = noteval["user"]["name"]
            if noteval["renoteId"] is not None:
                self._noteput(f"{name} [{username}] was renoted    noteId:{noteval['id']}", "-"*(self.screen.width-8))
            else:
                self._noteput(f"{name} [{username}] was noted    noteId:{noteval['id']}", "-"*(self.screen.width-8))
            if noteval["cw"] is not None:
                self._noteput("CW detect!","~"*(self.screen.width-8))
            self._noteput(noteval["text"],"")
            if len(noteval["files"]) != 0:
                self._noteput(f'{len(noteval["files"])} files')
            self._noteput(f'{noteval["renoteCount"]} renotes {noteval["repliesCount"]} replys {sum(noteval["reactions"].values())} reactions',
                          "  ".join(f'{i.replace("@.","")}[{noteval["reactions"][i]}]' for i in noteval["reactions"].keys()))
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

    def _noteput(self,*arg):
        for i in arg:
            self.note.value += str(i)+"\n"

    def _quit(self):
        self._scene.add_effect(PopUpDialog(self.screen,"Quit?", ["yes", "no"],on_close=self._quit_yes, has_shadow=True))

    def _quit_yes(self,arg):
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
        self.msk_ = msk
        self.set_theme(self.msk_.theme)
        layout = Layout([screen.width-21,1,20])
        self.add_layout(layout)
        self.txtbx = TextBox(screen.height-1,as_string=True,line_wrap=True)
        layout.add_widget(self.txtbx)
        self.txtbx.disabled=True
        layout.add_widget(VerticalDivider(screen.height),1)
        layout.add_widget(Button("Return",self.return_),2)
        layout.add_widget(Button("Change TL",self.poptl),2)
        layout.add_widget(Button("Change Theme",self.poptheme),2)
        layout.add_widget(Button("Version",self.version_),2)
        layout.add_widget(Button("Clear",self.clear_),2)
        self.fix()

    def version_(self):
        fonts = ["binary","chunky","contessa","cybermedium","hex","eftifont","italic","mini","morse","short"]
        randomint = randint(0,len(fonts))
        if randomint == len(fonts):
            mist_figs = "MisT\n"
        else:
            mist_figs = figlet_format("MisT",fonts[randomint])
        version = "v0.0.1"
        self._txtbxput(mist_figs+version,"","write by 35enidoi","@iodine53@misskey.io","")

    def clear_(self):
        self.txtbx.value = ""

    def poptl(self):
        self._scene.add_effect(PopUpDialog(self.screen,"Change TL", ["HTL", "LTL", "STL", "GTL"],on_close=self._ser_tl, has_shadow=True))

    def poptheme(self):
        self._scene.add_effect(PopUpDialog(self.screen,"Change Theme", ["default", "monochrome", "green", "bright"],on_close=self._ser_theme, has_shadow=True))

    def _ser_tl(self,arg):
        if arg == 0:
            if self.msk_.i is not None:
                self.msk_.tl = "HTL"
                self._txtbxput("change TL:HomeTL")
            else:
                self._txtbxput("HTL is credential required")
        elif arg == 1:
            self.msk_.tl = "LTL"
            self._txtbxput("change TL:LocalTL")
        elif arg == 2:
            if self.msk_.i is not None:
                self.msk_.tl = "STL"
                self._txtbxput("change TL:SocialTL")
            else:
                self._txtbxput("STL is credential required")
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
        raise ResizeScreenError("self error")

    def _txtbxput(self,*arg):
        for i in arg:
            self.txtbx.value += str(i)+"\n"

    @staticmethod
    def return_():
        raise NextScene("Main")

def wrap(screen, scene):
    scenes = [Scene([NoteView(screen, msk)], -1, name="Main"), Scene([ConfigMenu(screen, msk)], -1, name="Configration")]
    screen.play(scenes, stop_on_resize=True, start_scene=scene, allow_int=True)

msk = MkAPIs()
last_scene = None
while True:
    try:
        Screen.wrapper(wrap, catch_interrupt=True, arguments=[last_scene])
        sys.exit(0)
    except ResizeScreenError as e:
        last_scene = e.scene