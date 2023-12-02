from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.renderers import ImageFile
from asciimatics.widgets import Frame, Layout, TextBox, Button, PopUpDialog, VerticalDivider, Text, ListBox, PopupMenu
from asciimatics.exceptions import StopApplication, ResizeScreenError, NextScene
from misskey import Misskey, exceptions, MiAuth
from requests.exceptions import ReadTimeout, ConnectionError, ConnectTimeout, InvalidURL, HTTPError
import os

class MkAPIs():
    def __init__(self) -> None:
        # version
        # syoumi tekitouni ageteru noha naisyo
        self.version = 0.371
        # mistconfig load
        if os.path.isfile("mistconfig.conf"):
            self.mistconfig_put(True)
            if self.mistconfig["version"] < self.version:
                self.mistconfig["version"] = self.version
                if not self.mistconfig.get("default"):
                    self.mistconfig["default"] = {"theme":"default","defaulttoken":None}
                self.theme = self.mistconfig["default"]["theme"]
                self.mistconfig_put()
            else:
                self.theme = self.mistconfig["default"]["theme"]
        else:
            self.theme = "default"
            self.mistconfig = {"version":self.version,"default":{"theme":self.theme,"defaulttoken":None},"tokens":[]}
            self.mistconfig_put()
        # MisT settings
        self.tmp = []
        self.notes = []
        self.nowpoint = 0
        self.reacdb = None
        self.cfgtxts = ""
        self.crnotetxts = "Tab to change widget"
        self.crnoteconf = {"CW":None,"renoteId":None,"replyId":None}
        self.constcrnoteconf = self.crnoteconf.copy()
        # Misskey py settings
        if (default := self.mistconfig["default"]).get("defaulttoken") or default.get("defaulttoken") == 0:
            if len(self.mistconfig["tokens"]) != 0 and (len(self.mistconfig["tokens"]) > default["defaulttoken"]):
                self.i = self.mistconfig["tokens"][default["defaulttoken"]]["token"]
                self.instance = self.mistconfig["tokens"][default["defaulttoken"]]["instance"]
            else:
                self.i = None
                self.instance = "misskey.io"
        else:
            self.i = None
            self.instance = "misskey.io"
        self.mk = None
        self.tl = "LTL"
        self.tl_len = 10
        is_ok = self.reload()
        if not is_ok:
            self.i = None

    def mistconfig_put(self,loadmode=False):
        import json
        if loadmode:
            with open("mistconfig.conf", "r") as f:
                self.mistconfig = json.loads(f.read())
        else:
            with open("mistconfig.conf", "w") as f:
                f.write(json.dumps(self.mistconfig))

    def reload(self):
        bef_mk = self.mk
        try:
            self.mk=Misskey(self.instance,self.i)
            if self.i is not None:
                self.mk.i()
            return True
        except (exceptions.MisskeyAPIException, exceptions.MisskeyAuthorizeFailedException,
                ConnectionError, ReadTimeout, InvalidURL):
            self.mk = bef_mk
            return False

    def miauth_load(self):
        permissions = ["read:account","write:account","read:messaging","write:messaging","read:notifications",
                       "write:notifications","read:reactions","write:reactions","write:notes"]
        return MiAuth(self.instance,name="MisT",permission=permissions)

    def miauth_check(self,mia):
        try:
            self.i = mia.check()
            return True
        except (exceptions.MisskeyMiAuthFailedException, HTTPError):
            return False

    def get_i(self):
        try:
            return self.mk.i()
        except (exceptions.MisskeyAPIException, ConnectionError):
            return None

    def get_note(self,untilid=None,sinceid=None):
        try:
            if self.tl == "HTL":
                self.notes = self.mk.notes_timeline(self.tl_len,with_files=False,until_id=untilid,since_id=sinceid)
            elif self.tl == "LTL":
                self.notes = self.mk.notes_local_timeline(self.tl_len,with_files=False,until_id=untilid,since_id=sinceid)
            elif self.tl == "STL":
                self.notes = self.mk.notes_hybrid_timeline(self.tl_len,with_files=False,until_id=untilid,since_id=sinceid)
            elif self.tl == "GTL":
                self.notes = self.mk.notes_global_timeline(self.tl_len,with_files=False,until_id=untilid,since_id=sinceid)
            return True
        except (exceptions.MisskeyAPIException, ReadTimeout):
            self.notes = []
            return False

    def get_ntfy(self):
        try:
            return self.mk.i_notifications(100)
        except (exceptions.MisskeyAPIException, ReadTimeout):
            return None

    def get_reactiondb(self):
        import requests
        try:
            ret = requests.get(f'https://{self.instance}/api/emojis')
            if ret.status_code == 200:
                import json
                self.reacdb = {}
                for i in json.loads(ret.text)["emojis"]:
                    self.reacdb[i["name"]] = i["aliases"]
                    self.reacdb[i["name"]].append(i["name"])
            else:
                self.reacdb = None
        except ConnectTimeout:
            self.reacdb = None

    def note_update(self):
        beforenotes = self.notes.copy()
        noteid = self.notes[0]["id"]
        is_ok = self.get_note(noteid[0:8]+"zz")
        if is_ok:
            return True
        else:
            self.notes = beforenotes
            return False

    def noteshow(self,noteid):
        try:
            return self.mk.notes_show(noteid)
        except (exceptions.MisskeyAPIException, ReadTimeout):
            return None

    def get_instance_meta(self):
        try:
            self.meta = self.mk.meta()
            return True
        except (exceptions.MisskeyAPIException, ConnectTimeout):
            return False

    def get_instance_icon(self):
        import requests
        try:
            iconurl = self.meta["iconUrl"]
            returns = requests.get(iconurl)
            if returns.status_code == 200:
                import io
                icon = io.BytesIO(returns.content)
                return icon
            else:
                return "Error"
        except ConnectTimeout:
            return "Error"

    def create_note(self, text):
        try:
            return self.mk.notes_create(text, self.crnoteconf["CW"],
                                        renote_id=self.crnoteconf["renoteId"],
                                        reply_id=self.crnoteconf["replyId"])
        except exceptions.MisskeyAPIException:
            return None

    def create_renote(self, renoteid):
        try:
            return self.mk.notes_create(renote_id=renoteid)
        except exceptions.MisskeyAPIException:
            return None

    def create_reaction(self, noteid, reaction):
        try:
            return self.mk.notes_reactions_create(noteid, reaction)
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
        self._move_l = self.buttons[buttonnames.index("Move L")]
        self._move_r = self.buttons[buttonnames.index("Move R")]
        self.layout = layout
        self.layout2 = layout2

        # disable
        self.note.disabled = True
        moreind = buttonnames.index("More")
        noteupind = buttonnames.index("Noteupdate")
        if self.msk_.i is None:
            self.buttons[moreind].disabled = True
        else:
            self.buttons[moreind].disabled = False

        # fix
        self._note_reload()
        self.fix()

    def get_note(self,arg=-1):
        if arg == -1:
            if self.msk_.mk is None:
                self.popup("connect failed.\nPlease Instance recreate.", ["Ok"])
                return
            self.popup("note get from",["latest","until","since","return"],self.get_note)
            return
        elif arg == 0:
            untilid = None
            sinceid = None
        elif arg == 3:
            return
        else:
            if len(self.msk_.notes) == 0:
                self.popup("get note please(latest)",["Ok"])
                return
            elif arg == 1:
                untilid = self.msk_.notes[self.msk_.nowpoint]["id"]
                sinceid = None
            elif arg == 2:
                untilid = None
                sinceid = self.msk_.notes[self.msk_.nowpoint]["id"]
        self.msk_.get_note(untilid,sinceid)
        self.msk_.nowpoint=0
        self._note_reload()
    
    def noteupdate(self):
        is_ok = self.msk_.note_update()
        if is_ok:
            self._note_reload()
            self.popup("success", ["ok"])
        else:
            self.popup("something occured", ["ok"])

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
            self._noteput(f"{name} [{username}] was renoted    noteId:{note['id']}")
        else:
            self._noteput(f"{name} [{username}] was noted    noteId:{note['id']}")
        self.msk_.tmp.append("")
        if note["user"]["isBot"]:
            self.msk_.tmp[-1] += "isBot:True "
        if note["user"]["isCat"]:
            self.msk_.tmp[-1] += "isCat:True"
        if (a := self.msk_.tmp.pop()) != "":
            self._noteput(a)
        if note["user"].get("badgeRoles"):
            if len(note["user"]["badgeRoles"]) != 0:
                self._noteput("badgeRoles:["+",".join(i["name"] for i in note["user"]["badgeRoles"])+"]")
        self._noteput("-"*(self.screen.width-4))
        if note["text"] is None:
            if len(note["files"]) == 0:
                return
        if note["cw"] is not None:
            self._noteput("CW detect!",note["cw"],"~"*(self.screen.width-4))
        if note["user"]["isCat"]:
            self._noteput(note["text"].replace("な","にゃ").replace("ナ","ニャ"),"")
        else:
            self._noteput(note["text"],"")
        if len(note["files"]) != 0:
            self._noteput(f'{len(note["files"])} files')
        self._noteput(f'{note["renoteCount"]} renotes {note["repliesCount"]} replys {sum(note["reactions"].values())} reactions',
                        "  ".join(f'{i.replace("@.","")}[{note["reactions"][i]}]' for i in note["reactions"].keys()), "")

    def _noteput(self,*arg):
        for i in arg:
            self.note.value += str(i)+"\n"

    def pop_more(self):
        self.popup("?", ["Create Note", "Renote", "Reply", "Reaction", "Notification", "return"],self._ser_more)

    def pop_quit(self):
        self.popup("Quit?", ["yes", "no"],self._ser_quit)

    def _ser_more(self,arg):
        if arg == 0:
            # Create Note
            raise NextScene("CreateNote")
        elif arg == 1:
            # Renote or Quote
            if len(self.msk_.notes) == 0:
                self.popup("Please Note Get", ["Ok"])
            else:
                self.popup(f'Renote or Quote?', ["Renote", "Quote", "Return"],self._ser_rn)
        elif arg == 2:
            # Reply
            if len(self.msk_.notes) == 0:
                self.popup("Please Note Get", ["Ok"])
            else:
                if (noteval := self.msk_.notes[self.msk_.nowpoint]).get("renote"):
                    if noteval["text"] is None:
                        noteid = noteval["renote"]["id"]
                    else:
                        noteid = noteval["id"]
                else:
                    noteid = noteval["id"]
                self.msk_.crnoteconf["replyId"] = noteid
                raise NextScene("CreateNote")
        elif arg == 3:
            # Reaction
            if len(self.msk_.notes) == 0:
                self.popup("Please Note Get", ["Ok"])
            else:
                self.popup("from deck or search?", ["deck", "search", "return"], self._ser_reac)
        elif arg == 4:
            # Notification
            raise NextScene("Notification")

    def _ser_reac(self, arg):
        if arg == 0:
            # deck
            tokenindex = [char["token"] for char in self.msk_.mistconfig["tokens"]].index(self.msk_.i)
            if self.msk_.mistconfig["tokens"][tokenindex].get("reacdeck"):
                self._ser_reac_deck(-1)
            else:
                self.popup("Please create reaction deck", ["Ok"])
        elif arg == 1:
            # search
            self.msk_.tmp.append("searchmode")
            raise NextScene("SelReaction")

    def _ser_reac_deck(self,arg):
        tokenindex = [char["token"] for char in self.msk_.mistconfig["tokens"]].index(self.msk_.i)
        reacdeck = self.msk_.mistconfig["tokens"][tokenindex]["reacdeck"]
        if arg == -1:
            # initialize
            reacmenu = [(reacdeck[i], lambda x=i:self._ser_reac_deck(x)) for i in range(len(reacdeck))]
            reacmenu.insert(0, ("Return", lambda: None))
            self._scene.add_effect(PopupMenu(self.screen,reacmenu, self.screen.width//3, 0))
        else:
            # Create reaction
            if (noteval := self.msk_.notes[self.msk_.nowpoint]).get("renote"):
                if noteval["text"] is None:
                    noteid = noteval["renote"]["id"]
                else:
                    noteid = noteval["id"]
            else:
                noteid = noteval["id"]
            is_create_seccess = self.msk_.create_reaction(noteid,f":{reacdeck[arg]}:")
            if is_create_seccess:
                self.popup('Create success! :)', ["Ok"])
            else:
                self.popup("Create fail :(", ["Ok"])

    def _ser_rn(self, arg):
        if arg == 0:
            # Renote
            if (noteval := self.msk_.notes[self.msk_.nowpoint]).get("renote"):
                if noteval["text"] is None:
                    noteval = noteval["renote"]
                    username = noteval["user"]["name"]
                    noteid = noteval["id"]
                else:
                    username = noteval["user"]["name"]
                    noteid = noteval["id"]
            else:
                username = noteval["user"]["name"]
                noteid = noteval["id"]
            if len(noteval["text"]) <= 15:
                text = noteval["text"]
            else:
                text = noteval["text"][0:16]+"..."
            self.popup(f'Renote this?\nnoteId:{noteid}\nname:{username}\ntext:{text}', ["Ok","No"],on_close=self._ser_renote)
        if arg == 1:
            # Quote
            if (noteval := self.msk_.notes[self.msk_.nowpoint]).get("renote"):
                if noteval["text"] is None:
                    noteid = noteval["renote"]["id"]
                else:
                    noteid = noteval["id"]
            else:
                noteid = noteval["id"]
            self.msk_.crnoteconf["renoteId"] = noteid
            raise NextScene("CreateNote")

    def _ser_renote(self, arg):
        if arg == 0:
            if (noteval := self.msk_.notes[self.msk_.nowpoint]).get("renote"):
                if noteval["text"] is None:
                    noteid = noteval["renote"]["id"]
                else:
                    noteid = noteval["id"]
            else:
                noteid = noteval["id"]
            createnote = self.msk_.create_renote(noteid)
            if createnote is not None:
                self.popup('Create success! :)', ["Ok"])
            else:
                self.popup("Create fail :(", ["Ok"])

    def popup(self,txt,button,on_close=None):
        self._scene.add_effect(PopUpDialog(self.screen,txt,button,on_close))

    def _ser_quit(self,arg):
        if arg == 0:
            self.msk_.mistconfig_put()
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
        self.set_theme(self.msk_.theme)

        # txts create
        self.txtbx = TextBox(screen.height-1,as_string=True,line_wrap=True)
        self.txt = Text()
        self.txtbx.value = self.msk_.cfgtxts

        # buttons create
        buttonnames = ("Return", "Change TL", "Change Theme", "Reaction deck",
                       "TOKEN", "Instance", "Current","Version",
                       "Clear","Refresh", "OK")
        onclicks = (self.return_, self.poptl, self.poptheme, self.reactiondeck,
                    self.poptoken, self.instance_, self.current, self.version_,
                    self.clear_, self.refresh_,self.ok_)
        self.buttons = [Button(buttonnames[i],onclicks[i]) for i in range(len(buttonnames))]

        # Layout create
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
        from util import mistfigleter
        self._txtbxput(mistfigleter()+"v"+str(self.msk_.version),"","write by @iodine53@misskey.io","")

    def current(self):
        self._txtbxput(f"Instance:{self.msk_.instance}")
        if self.msk_.i is None:
            self._txtbxput("TOKEN:None","")
        else:
            user = self.msk_.get_i()
            if user is not None:
                self._txtbxput("TOKEN:Available",f' name:{user["name"]}',f' username:{user["username"]}',"")
            else:
                self._txtbxput("TOKEN:Available","fail to get userinfo :(","")

    def clear_(self):
        self.txtbx.value = ""
        self.msk_.cfgtxts = ""

    def _txtbxput(self,*arg):
        for i in arg:
            self.txtbx.value += str(i)+"\n"
        self.msk_.cfgtxts = self.txtbx.value

    def reactiondeck(self, arg = -1):
        if arg == -1:
            # initialize
            if self.msk_.i is None:
                self.popup("Please set TOKEN", ["OK"])
            else:
                self.popup("check deck or add deck?", ["check deck", "del deck", "add deck", "return"], self.reactiondeck)
        elif arg == 0:
            # check deck
            tokenindex = [char["token"] for char in self.msk_.mistconfig["tokens"]].index(self.msk_.i)
            if not (nowtoken := self.msk_.mistconfig["tokens"][tokenindex]).get("reacdeck"):
                self.popup("Please create reaction deck", ["Ok"])
            else:
                self._scene.add_effect(PopupMenu(self.screen,[(char, lambda: None) for char in nowtoken["reacdeck"]], self.screen.width//3, 0))
        elif arg == 1:
            # del deck
            tokenindex = [char["token"] for char in self.msk_.mistconfig["tokens"]].index(self.msk_.i)
            if not (nowtoken := self.msk_.mistconfig["tokens"][tokenindex]).get("reacdeck"):
                self.popup("Please create reaction deck", ["Ok"])
            else:
                self.reactiondel(-1)
        elif arg == 2:
            # add deck
            self.msk_.tmp.append("deck")
            raise NextScene("SelReaction")
    
    def reactiondel(self, arg):
        tokenindex = [char["token"] for char in self.msk_.mistconfig["tokens"]].index(self.msk_.i)
        reacdeck = self.msk_.mistconfig["tokens"][tokenindex]["reacdeck"]
        if arg == -1:
            # initialize
            reacmenu = [(reacdeck[i], lambda x=i:self.reactiondel(x)) for i in range(len(reacdeck))]
            if len(reacmenu) == 0:
                self.msk_.mistconfig_put()
            else:
                reacmenu.insert(0, ("Return", lambda: self.msk_.mistconfig_put()))
                self._scene.add_effect(PopupMenu(self.screen,reacmenu, self.screen.width//3, 0))
        else:
            # del reaction
            reacdeck.pop(arg)
            self.reactiondel(-1)

    def poptl(self):
        self.popup("Change TL", ["HTL", "LTL", "STL", "GTL"],self._ser_tl)

    def poptheme(self):
        self.popup("Change Theme", ["default", "monochrome", "green", "bright", "return"],self._ser_theme)

    def poptoken(self):
        self.popup(f"How to?\ncurrent instance:{self.msk_.instance}", ["Create", "Select", "return"],self._ser_token)

    def _ser_tl(self,arg):
        if arg == 0:
            # HTL
            if self.msk_.i is not None:
                self.msk_.tl = "HTL"
                self._txtbxput("change TL:HomeTL")
            else:
                self._txtbxput("HTL is TOKEN required")
        elif arg == 1:
            # LTL
            self.msk_.tl = "LTL"
            self._txtbxput("change TL:LocalTL")
        elif arg == 2:
            # STL
            if self.msk_.i is not None:
                self.msk_.tl = "STL"
                self._txtbxput("change TL:SocialTL")
            else:
                self._txtbxput("STL is TOKEN required")
        elif arg == 3:
            # GTL
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
        self.msk_.mistconfig["default"]["theme"] = self.msk_.theme
        self.msk_.mistconfig_put()
        raise ResizeScreenError("self error")

    def _ser_token(self,arg):
        if arg == 0:
            # Create
            self.popup(f"MiAuth or write TOKEN?",["MiAuth", "TOKEN", "return"],self._ser_token_create)
        elif arg == 1:
            # Select
            if len(self.msk_.mistconfig["tokens"]) == 0:
                self.popup(f"Create TOKEN please.", ["ok"])
            else:
                self._ser_token_search(-1)
    
    def _ser_token_create(self,arg):
        if arg == 0:
            from util import pypcopy, webshow
            # MiAuth
            self.msk_.tmp.append(self.msk_.miauth_load())
            url = self.msk_.tmp[-1].generate_url()
            webshow(url)
            space = "      \n      "
            lens = self.screen.width//2
            lines = len(url)//lens
            url = space.split("\n")[0]+space.join([url[i*lens:(i+1)*lens] for i in range(lines)])
            copysuccess = pypcopy(url)
            self.popup(f"miauth url\n\n{url}\n\n"+("cliped!" if copysuccess else ""), ["check ok"],self.miauth_get)
        elif arg == 1:
            # TOKEN
            self._txtbxput("write your TOKEN")
            self.msk_.tmp.append("TOKEN")
            self._disables()
    
    def _ser_token_search(self,arg):
        token = self.msk_.mistconfig["tokens"]
        button = ["L", "R", "Select", "Delete", "Set def", "unset def"]
        if arg == -1:
            # initialize
            self.msk_.tmp.append(0)
            mes = f'<1/{len(token)}>\n\nSelect\nname:{token[0]["name"]}\ninstance:{token[0]["instance"]}\ntoken:{token[0]["token"][0:8]}...'
            self.popup(mes, button, self._ser_token_search)
        elif arg == 0:
            # L
            num = self.msk_.tmp.pop()
            if num == 0:
                self.msk_.tmp.append(0)
                headmes = "Too Left.\n"
            else:
                num -= 1
                self.msk_.tmp.append(num)
                headmes = "Select\n"
            mes = f'<{num+1}/{len(token)}>\n\n{headmes}name:{token[num]["name"]}\ninstance:{token[num]["instance"]}\ntoken:{token[num]["token"][0:8]}...'
            self.popup(mes, button,self._ser_token_search)
        elif arg == 1:
            # R
            num = self.msk_.tmp.pop()
            if num+1 == len(token):
                self.msk_.tmp.append(num)
                headmes = "Too Right.\n"
            else:
                num += 1
                self.msk_.tmp.append(num)
                headmes = "Select\n"
            mes = f'<{num+1}/{len(token)}>\n\n{headmes}name:{token[num]["name"]}\ninstance:{token[num]["instance"]}\ntoken:{token[num]["token"][0:8]}...'
            self.popup(mes, button,self._ser_token_search)
        elif arg == 2:
            # Select
            num = self.msk_.tmp.pop()
            userinfo = token[num]
            self._txtbxput(f'select user:{userinfo["name"]}',f'current instance:{userinfo["instance"]}',"")
            self.msk_.i = userinfo["token"]
            self.msk_.instance = userinfo["instance"]
            is_ok = self.msk_.reload()
            if is_ok:
                self._txtbxput("connect ok!","")
                self.refresh_(True)
            else:
                self.msk_.i = None
                self._txtbxput("connect fail :(","")
        elif arg == 3:
            # Delete
            num = self.msk_.tmp[-1]
            headmes = "Delete this?\n"
            mes = f'<{num+1}/{len(token)}>\n\n{headmes}name:{token[num]["name"]}\ninstance:{token[num]["instance"]}\ntoken:{token[num]["token"][0:8]}...'
            self.popup(mes, ["Yes","No"],self._ser_token_delete)
        elif arg == 4:
            # Set
            num = self.msk_.tmp[-1]
            headmes = "set to default?\n"
            mes = f'<{num+1}/{len(token)}>\n\n{headmes}name:{token[num]["name"]}\ninstance:{token[num]["instance"]}\ntoken:{token[num]["token"][0:8]}...'
            self.popup(mes,["Yes","No"],self._ser_token_default)
        elif arg == 5:
            # Unset
            num = self.msk_.tmp[-1]
            if self.msk_.mistconfig["default"]["defaulttoken"] is None:
                headmes = "default token is none\n"
            else:
                self.msk_.mistconfig["default"]["defaulttoken"] = None
                self.msk_.mistconfig_put()
                headmes = "unset success!\n"
            mes = f'<{num+1}/{len(token)}>\n\n{headmes}name:{token[num]["name"]}\ninstance:{token[num]["instance"]}\ntoken:{token[num]["token"][0:8]}...'
            self.popup(mes, button,self._ser_token_search)

    def _ser_token_default(self,arg):
        num = self.msk_.tmp[-1]
        if arg == 0:
            self.msk_.mistconfig["default"]["defaulttoken"] = num
            self.msk_.mistconfig_put()
            self._ser_token_search(2)
        else:
            self._ser_token_search(-1)

    def _ser_token_delete(self,arg):
        num = self.msk_.tmp.pop()
        if arg == 0:
            if (deftkindex := self.msk_.mistconfig["default"]["defaulttoken"]) is not None:
                if num < deftkindex:
                    self.msk_.mistconfig["default"]["defaulttoken"] -= 1
                elif num == deftkindex:
                    self.msk_.mistconfig["default"]["defaulttoken"] = None
            self.msk_.mistconfig["tokens"].pop(num)
            self.msk_.mistconfig_put()
            if len(self.msk_.mistconfig["tokens"]) == 0:
                return
        self._ser_token_search(-1)

    def miauth_get(self,arg):
        if arg == 0:
            is_ok = self.msk_.miauth_check(self.msk_.tmp[-1])
            if is_ok:
                text = "MiAuth check Success!\n"
                self.msk_.reload()
                userinfo = self.msk_.get_i()
                if userinfo is not None:
                    name = userinfo["name"]
                    text += f'Hello {name}'
                else:
                    text += "fail to get userinfo :("
                    name = "fail to get"
                userdict = {"name":name,"instance":self.msk_.instance,"token":self.msk_.i}
                self.msk_.mistconfig["tokens"].append(userdict)
                self.msk_.mistconfig_put()
                self.msk_.notes = []
                self.msk_.reacdb = None
                self.popup(text, ["Ok"], self.refresh_)
                self.msk_.tmp.pop()
            else:
                text = "MiAuth check Fail :(\ntry again?"
                self.popup(text, ["again", "return"], self.miauth_get)
        else:
            self.msk_.tmp.pop()

    def instance_(self, select=-1):
        if select == -1:
            if self.msk_.i is not None:
                self.popup("TOKEN detect!\nchange instance will delete TOKEN.\nOk?", ["Ok","No"],on_close=self.instance_)
            else:
                self.msk_.tmp.append("INSTANCE")
                self._txtbxput("input instance such as 'misskey.io' 'misskey.backspace.fm'", f"current instance:{self.msk_.instance}","")
                self._disables()
        elif select == 0:
            self.msk_.i = None
            self.instance_()

    def ok_(self):
        ok_value = self.msk_.tmp.pop()
        if ok_value == "TOKEN":
            self.msk_.i = self.txt.value
            is_ok = self.msk_.reload()
            if is_ok:
                self._txtbxput("TOKEN check OK :)")
                i = self.msk_.get_i()
                if i is None:
                    name = "get fail"
                    self._txtbxput("fail to get your info :(")
                else:
                    name = i["name"]
                    self._txtbxput(f"Hello {name}!")
                self.msk_.mistconfig["tokens"].append({"name":name, "instance":self.msk_.instance, "token":self.msk_.i})
                self.msk_.mistconfig_put()
                self.refresh_(True)
            else:
                self.msk_.i = ""
                self._txtbxput("TOKEN check fail :(")
        elif ok_value == "INSTANCE":
            before_instance = self.msk_.instance
            self.msk_.instance = self.txt.value
            is_ok = self.msk_.reload()
            if is_ok:
                self._txtbxput("instance connected! :)")
                is_ok = self.msk_.get_instance_meta()
                if is_ok:
                    icon_bytes = self.msk_.get_instance_icon()
                    if icon_bytes == "Error":
                        self._txtbxput("error occured while get icon :(")
                    else:
                        icon = ImageFile(icon_bytes,self.screen.height//2)
                        self._txtbxput(icon)
                else:
                    self._txtbxput("error occured while get meta :(")
            else:
                self.msk_.instance = before_instance
                self._txtbxput("instance connect fail :(")
            self._txtbxput(f"current instance:{self.msk_.instance}","")
            self.refresh_(True)
        self._disables(True)

    def _disables(self,rev=False):
        if rev:
            self.txt.value = ""
        self.txt.disabled = rev
        for i in self.buttons:
            i.disabled = (not rev)
        self.buttons[-1].disabled = rev
        if rev:
            self.switch_focus(self.layout,2,0)
        else:
            self.switch_focus(self.layout,2,len(self.buttons))

    def refresh_(self, notedel=False):
        if notedel:
            self.msk_.reacdb = None
            self.msk_.notes = []
        raise ResizeScreenError("self error", self._scene)

    def popup(self,txt,button,on_close=None):
        self._scene.add_effect(PopUpDialog(self.screen,txt,button,on_close))

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
        buttonnames = ("Note Create", "hug punch", "return", "MoreConf")
        on_click = (self.popcreatenote, self.hug_punch, self.return_, self.conf_)
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
    
    def hug_punch(self):
        from random import randint
        hugpunchs = ["(Δ・x・Δ)","v('ω')v","(=^・・^=)","✌️(´･_･`)✌️",
                     "( ‘ω’ و(و “","ԅ( ˘ω˘ ԅ)ﾓﾐﾓﾐ","🐡( '-' 🐡 )ﾌｸﾞﾊﾟﾝﾁ!!!!","(｡>﹏<｡)"]
        self.txtbx.value += hugpunchs[randint(0,len(hugpunchs)-1)]

    def popcreatenote(self):
        self._scene.add_effect(PopUpDialog(self.screen,"Are you sure about that?", ["Sure", "No"],self._ser_createnote))

    def _ser_createnote(self,arg):
        if arg == 0:
            return_ = self.msk_.create_note(self.txtbx.value)
            if return_ is not None:
                self._scene.add_effect(PopUpDialog(self.screen,"Create note success :)", ["Ok"],on_close=self.return_))
                self.msk_.crnotetxts = "Tab to change widget"
                self.txtbx.value = self.msk_.crnotetxts
                self.msk_.crnoteconf = self.msk_.constcrnoteconf.copy()
            else:
                self._scene.add_effect(PopUpDialog(self.screen,"Create note fail :(", ["Ok"]))

    def _ser_ret(self,arg):
        if arg == 0:
            self.msk_.crnoteconf["renoteId"] = None
            self.msk_.crnoteconf["replyId"] = None
            self.return_()

    def popup(self,txt,button,on_close=None):
        self._scene.add_effect(PopUpDialog(self.screen,txt,button,on_close))

    def return_(self,*_):
        if (n := self.msk_.crnoteconf)["renoteId"] is not None:
            self.popup("renoteId detect!\nif return, it will delete\n are you sure about that?",["sure","no"],self._ser_ret)
        elif n["replyId"] is not None:
            self.popup("replyId detect!\nif return, it will delete\n are you sure about that?",["sure","no"],self._ser_ret)
        else:
            raise NextScene("Main")

    @staticmethod
    def conf_():
        raise NextScene("CreNoteConf")

class CreateNoteConfig(Frame):
    def __init__(self, screen, msk):
        super(CreateNoteConfig, self).__init__(screen,
                                    screen.height,
                                    screen.width,
                                    title="CreateNoteCfg",
                                    reduce_cpu=True,
                                    can_scroll=False,
                                    on_load=self.nowconf)
        # initialize
        self.msk_ = msk
        self.set_theme(self.msk_.theme)

        # txt create
        self.txtbx = TextBox(screen.height-1,as_string=True,line_wrap=True)
        self.txt = Text()

        # buttons
        buttonnames = ("return","CW","renoteId","replyId","OK")
        onclicks = (self.return_,self.cw,self.renoteid,self.replyid,self.ok_)
        self.buttons = [Button(buttonnames[i],onclicks[i]) for i in range(len(buttonnames))]

        # layout
        self.layout = Layout([screen.width,2,20])
        self.add_layout(self.layout)

        # add widget
        self.layout.add_widget(self.txtbx,0)
        self.layout.add_widget(VerticalDivider(screen.height),1)
        for i in self.buttons:
            self.layout.add_widget(i,2)
        self.layout.add_widget(self.txt,2)

        # disables
        self.txtbx.disabled = True
        self.txt.disabled = True
        self.buttons[-1].disabled = True

        # fix
        self.nowconf()
        self.fix()
    
    def cw(self):
        self.msk_.tmp.append("cw")
        self.txt.value = "" if self.msk_.crnoteconf["CW"] is None else self.msk_.crnoteconf["CW"]
        self._disables()
    
    def renoteid(self):
        self.msk_.tmp.append("renote")
        self.txt.value = "" if self.msk_.crnoteconf["renoteId"] is None else self.msk_.crnoteconf["renoteId"]
        self._disables()

    def replyid(self):
        self.msk_.tmp.append("reply")
        self.txt.value = "" if self.msk_.crnoteconf["replyId"] is None else self.msk_.crnoteconf["replyId"]
        self._disables()

    def ok_(self):
        if (ok_value := self.msk_.tmp.pop()) == "cw":
            self.msk_.crnoteconf["CW"] = None if self.txt.value == "" else self.txt.value
        elif ok_value == "renote":
            if self.txt.value == "":
                self.msk_.crnoteconf["renoteId"] = None
            else:
                note = self.msk_.noteshow(self.txt.value)
                if note is not None:
                    self.popup(f'user:{note["user"]["name"]}\ntext:{note["text"]}',["ok"])
                    self.msk_.crnoteconf["renoteId"] = self.txt.value
                else:
                    self.popup("note show fail :(\nmaybe this noteId is unavailable",["ok"])
                    self.msk_.crnoteconf["renoteId"] = None
        elif ok_value == "reply":
            if self.txt.value == "":
                self.msk_.crnoteconf["replyId"] = None
            else:
                note = self.msk_.noteshow(self.txt.value)
                if note is not None:
                    self.popup(f'user:{note["user"]["name"]}\ntext:{note["text"]}',["ok"])
                    self.msk_.crnoteconf["replyId"] = self.txt.value
                else:
                    self.popup("note show fail :(\nmaybe this noteId is unavailable",["ok"])
                    self.msk_.crnoteconf["replyId"] = None
        self.nowconf()
        self._disables(True)

    def _disables(self,rev=False):
        if rev:
            self.txt.value = ""
        self.txt.disabled = rev
        for i in self.buttons:
            i.disabled = (not rev)
        self.buttons[-1].disabled = rev
        if rev:
            self.switch_focus(self.layout,2,0)
        else:
            self.switch_focus(self.layout,2,len(self.buttons))

    def nowconf(self):
        self.txtbx.value = ""
        for i in self.msk_.crnoteconf.keys():
            self.txtbx.value += f"{i}:{self.msk_.crnoteconf[i]}\n"

    def popup(self,txt,button,on_close=None):
        self._scene.add_effect(PopUpDialog(self.screen,txt,button,on_close))

    @staticmethod
    def return_():
        raise NextScene("CreateNote")

class SelectReaction(Frame):
    def __init__(self, screen, msk):
        super(SelectReaction, self).__init__(screen,
                                      screen.height,
                                      screen.width,
                                      title="SelectReaction",
                                      reduce_cpu=True,
                                      can_scroll=False,
                                      on_load=self.load)
        # initialize
        self.msk_ = msk
        self.set_theme(self.msk_.theme)

        # txtbox create
        self.txtbx = Text(on_change=self.search)

        # listbox create
        self.lstbx = ListBox(self.screen.height-3, [], name="emojilist", on_select=self.select)

        # buttons create
        buttonnames = ("GetDB","return")
        on_click = (self.getdb,self.return_)
        self.buttons = [Button(buttonnames[i],on_click[i]) for i in range(len(buttonnames))]

        # Layout create
        layout = Layout([100])
        layout2 = Layout([1 for _ in range(len(self.buttons)+1)])
        self.add_layout(layout)
        self.add_layout(layout2)

        # add widget
        layout.add_widget(self.lstbx)
        layout2.add_widget(self.txtbx)
        for i in range(len(self.buttons)):
            layout2.add_widget(self.buttons[i],i+1)

        # fix
        self.fix()

    def load(self):
        if len(self.msk_.tmp) != 0:
            if (tmpval := self.msk_.tmp[-1]) == "searchmode":
                self.msk_.tmp.pop()
                self.flag = "search"
            elif tmpval == "deck":
                self.msk_.tmp.pop()
                self.flag = "deckadd"
            else:
                self.flag = ""
        else:
            self.flag = ""

    def search(self):
        if self.msk_.reacdb is None:
            self.lstbx.options = [("DB is None, Please GetDB.",0)]
            self.txtbx.disabled = True
        else:
            self.lstbx.options = []
            self.txtbx.disabled = False
            n = 0
            for i in (reacdb := self.msk_.reacdb).keys():
                if any(self.txtbx.value in r for r in reacdb[i]):
                    self.lstbx.options.append((i, len(self.lstbx.options)))
                    n += 1
                if n >= self.screen.height-3:
                    break

    def select(self):
        self.save()
        index = self.data["emojilist"]
        if (reaction := self.lstbx.options[index][0]) == "DB is None, Please GetDB.":
            pass
        else:
            if self.flag == "search":
                if (noteval := self.msk_.notes[self.msk_.nowpoint]).get("renote"):
                    if noteval["text"] is None:
                        noteid = noteval["renote"]["id"]
                    else:
                        noteid = noteval["id"]
                else:
                    noteid = noteval["id"]
                is_create_seccess = self.msk_.create_reaction(noteid,f":{reaction}:")
                if is_create_seccess:
                    self.popup('Create success! :)', ["Ok"], self.return_)
                else:
                    self.popup("Create fail :(", ["Ok"], self.return_)
            elif self.flag == "deckadd":
                tokenindex = [char["token"] for char in self.msk_.mistconfig["tokens"]].index(self.msk_.i)
                if not (nowtoken := self.msk_.mistconfig["tokens"][tokenindex]).get("reacdeck"):
                    nowtoken["reacdeck"] = []
                if reaction in nowtoken["reacdeck"]:
                    self.popup("this reaction already in deck", ["Ok"])
                else:
                    nowtoken["reacdeck"].append(reaction)
                    self.popup(f"reaction added\nname:{reaction}",["Ok"])

    def getdb(self):
        self.msk_.get_reactiondb()
        if self.msk_.reacdb is None:
            self.popup("GetDB fail :(",["Ok"])
        else:
            self.popup("GetDB success!",["Ok"])
            self.search()
    
    def popup(self,txt,button,on_close=None):
        self._scene.add_effect(PopUpDialog(self.screen,txt,button,on_close))

    def return_(self,*_):
        self.flag = ""
        self.txtbx.value = ""
        raise NextScene("Main")

class Notification(Frame):
    def __init__(self, screen, msk):
        super(Notification, self).__init__(screen,
                                      screen.height,
                                      screen.width,
                                      title="Notification",
                                      reduce_cpu=True,
                                      can_scroll=False)
        # initialize
        self.msk_ = msk
        self.set_theme(self.msk_.theme)

        # txtbox create
        self.txtbx = TextBox(screen.height-3, as_string=True, line_wrap=True, readonly=True)
        self.txtbx.auto_scroll = False
        self.txtbx.value = "Tab to change widget"

        # buttons create
        buttonnames = ("Get ntfy", "return")
        on_click = (self.get_ntfy, self.return_)
        self.buttons = [Button(buttonnames[i],on_click[i]) for i in range(len(buttonnames))]

        # Layout create
        layout = Layout([14,2,self.screen.width-16])
        self.add_layout(layout)

        # add widget
        for i in range(len(self.buttons)):
            layout.add_widget(self.buttons[i],0)
        layout.add_widget(VerticalDivider(self.screen.height),1)
        layout.add_widget(self.txtbx,2)

        #fix
        self.fix()
    
    def get_ntfy(self):
        self.txtbx.value = ""
        ntfys = self.msk_.get_ntfy()
        if ntfys is None:
            self.txtbx.value = "Fail to get notifications"
            self._scene.add_effect(PopUpDialog(self.screen,"Fail to get ntfy", ["Ok"]))
        else:
            checkntfytype = {"follow":[],"mention":[],"notes":{},"else":[]}
            for i in ntfys:
                if (ntfytype := i["type"]) == "follow":
                    checkntfytype["follow"].append(i)
                elif ntfytype == "mention":
                    checkntfytype["mention"].append(i)
                else:
                    if not i.get("note"):
                        continue
                    if (ntfytype == "renote") or (ntfytype == "quote"):
                        if i["note"]["renote"]["id"] not in checkntfytype["notes"]:
                            checkntfytype["notes"][i["note"]["renote"]["id"]] = {"value":i["note"]["renote"],"ntfy":[]}
                        checkntfytype["notes"][i["note"]["renote"]["id"]]["ntfy"].append(i)
                        continue
                    if ntfytype == "reply":
                        if i["note"]["reply"]["id"] not in checkntfytype["notes"]:
                            checkntfytype["notes"][i["note"]["reply"]["id"]] = {"value":i["note"]["reply"],"ntfy":[]}
                        checkntfytype["notes"][i["note"]["reply"]["id"]]["ntfy"].append(i)
                        continue
                    if ntfytype == "reaction":
                        if i["note"]["id"] not in checkntfytype["notes"]:
                            checkntfytype["notes"][i["note"]["id"]] = {"value":i["note"],"ntfy":[]}
                        checkntfytype["notes"][i["note"]["id"]]["ntfy"].append(i)
                    else:
                        checkntfytype["else"].append(i)
            if len(follower := checkntfytype["follow"]) != 0:
                self._txtbxput("Follow comming!","\n".join(char["user"]["name"] if char["user"].get("name") else char["user"]["username"] for char in follower),"")
            if len(mentions := checkntfytype["mention"]) != 0:
                self._txtbxput("mention comming!",
                               "\n\n".join(char["user"]["name"]+"\n"+char["note"]["text"].replace("な","にゃ").replace("ナ","ニャ") if char["user"]["isCat"] else char["note"]["text"] for char in mentions),
                               "")
            if len(notes := checkntfytype["notes"]) != 0:
                for i in notes:
                    headtext = f"noteid:{i}\n"+f'text:{str(notes[i]["value"]["text"].replace("な","にゃ").replace("ナ","ニャ") if notes[i]["value"]["user"]["isCat"] else notes[i]["value"]["text"])}\n'
                    txt = []
                    for i in notes[i]["ntfy"]:
                        if i.get("user"):
                            if i["user"]["name"] is None:
                                username = i["user"]["username"]
                            else:
                                username = i["user"]["name"]
                        else:
                            username = "Deleted user?"
                            i["user"] = {"isCat":False}
                        if (nttype := i["type"]) == "reply":
                            txt.append(f"{username} was reply")
                            txt.append(i["note"]["text"].replace("な","にゃ").replace("ナ","ニャ") if i["user"]["isCat"] else i["note"]["text"])
                        elif nttype == "quote":
                            txt.append(f"{username} was quoted")
                            txt.append(i["note"]["text"].replace("な","にゃ").replace("ナ","ニャ") if i["user"]["isCat"] else i["note"]["text"])
                        elif nttype == "renote":
                            txt.append(f"{username} was renoted")
                        elif nttype == "reaction":
                            txt.append(f'{username} was reaction [{i["reaction"]}]')
                    self._txtbxput(headtext,*txt,"\n")
            self._scene.add_effect(PopUpDialog(self.screen,"Success", ["Ok"]))

    def _txtbxput(self,*arg):
        for i in arg:
            self.txtbx.value += str(i)+"\n"
    
    @staticmethod
    def return_():
        raise NextScene("Main")

def wrap(screen, scene):
    scenes = [Scene([NoteView(screen, msk)], -1, name="Main"),
              Scene([ConfigMenu(screen, msk)], -1, name="Configration"),
              Scene([CreateNote(screen, msk)], -1, name="CreateNote"),
              Scene([Notification(screen, msk)], -1, name="Notification"),
              Scene([CreateNoteConfig(screen, msk)], -1, name="CreNoteConf"),
              Scene([SelectReaction(screen, msk)], -1, name="SelReaction")]
    screen.play(scenes, stop_on_resize=True, start_scene=scene, allow_int=True)

def main():
    global msk
    msk = MkAPIs()
    last_scene = None
    while True:
        try:
            Screen.wrapper(wrap, arguments=[last_scene])
            os._exit(0)
        except ResizeScreenError as e:
            last_scene = e.scene

if __name__ == "__main__":
    main()