# polibが必要

import polib
import os
from pprint import pprint

def getpath(path:str) -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__),f'./{path}'))

ps = polib.pofile(getpath("messages.pot"))
newpo = polib.POFile()
newpo.metadata = ps.metadata
# pprint(newpo.metadata)
# print()
for entry in [e for e in ps if not e.obsolete]:
    ent = polib.POEntry(msgid=entry.msgid, msgstr=" ".join([hex(ord(s))[2:] if s not in ("{", "}","\n") else s for s in entry.msgid]).replace("{ }", "{}"))
    newpo.append(ent)
# for entry in [e for e in newpo if not e.obsolete]:
#     print(entry.msgid, entry.msgstr)

if not os.path.isdir(getpath("en_ASCII_HEX/LC_MESSAGES")):
    os.mkdir(getpath("en_ASCII_HEX"))
    os.mkdir(getpath("en_ASCII_HEX/LC_MESSAGES"))
newpo.save(getpath("en_ASCII_HEX/LC_MESSAGES/messages.po"))
newpo.save_as_mofile(getpath("en_ASCII_HEX/LC_MESSAGES/messages.mo"))