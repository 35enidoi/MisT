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
                msk.note_update()

        await asyncio.to_thread(__anupd_ope, self)