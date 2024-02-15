from .daemon import Daemon
import asyncio

@Daemon.newd
class Anupd:
    "Auto note update daemon"
    def __init__(self) -> None:
        self.wheeld_ope_add("anupd", self._anupd_ope)
        self.anupd()
        super().__init__()
    
    @Daemon.daemon_main
    async def anupd(self):
        while True:
            await asyncio.sleep(5)
            self.wheeld_ope_put("anupd")

    async def _anupd_ope(self):

        @Daemon.glb_getter
        def __anupd_ope(msk, _):
            if len(msk.notes) != 0:
                CUTNOTELEN = 20
                CUTPOINT = 10
                ntlen = len(msk.notes)
                flag = False
                if ntlen == 100 and msk.nowpoint <= CUTPOINT:
                    ntlen = 100-CUTNOTELEN
                    flag = True
                btmnoteid = msk.notes[ntlen-1]["id"]
                notes = msk.get_note(sinceid=btmnoteid[:-2]+"aa")
                if notes is not None:
                    beforenotes = msk.notes
                    if flag:
                        beforenotes = beforenotes[:100-CUTNOTELEN]
                    ints = {i["id"] for i in beforenotes}&{i["id"] for i in notes}
                    if len(ints) >= len(beforenotes)-2 and len(ints) != 0:
                        if flag:
                            msk.nowpoint += CUTNOTELEN
                        msk.nowpoint += len(notes)-len(msk.notes)
                        msk.notes = notes

        await asyncio.to_thread(__anupd_ope, self)