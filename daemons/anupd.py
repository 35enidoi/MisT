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
                btmnoteid = msk.notes[len(msk.notes)-1]["id"]
                notes = msk.get_note(sinceid=btmnoteid[:-2]+"aa")
                if notes is not None:
                    ints = {i["id"] for i in msk.notes}&{i["id"] for i in notes}
                    if len(ints) >= len(msk.notes)-2 and len(ints) != 0:
                        msk.nowpoint += len(notes)-len(msk.notes)
                        msk.notes = notes

        await asyncio.to_thread(__anupd_ope, self)