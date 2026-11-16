from misskey_tui.model.mkapi import MkAPIs
from misskey_tui.model.config import Config
from misskey_tui.model.timeline import TimelineService


# version
# syoumi tekitouni ageteru noha naisyo
VERSION = 0.42


class Model:
    def __init__(self):
        self.config = Config(VERSION)
        self.mkapi = MkAPIs(self.config)
        self.timeline_service = TimelineService(self.mkapi)
