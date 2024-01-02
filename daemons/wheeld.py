from .daemon import Daemon
import asyncio

@Daemon.newd
class Wheeld:
    def __init__(self) -> None:
        self._wheeld_queue = asyncio.Queue()
        self._wheeld_ope = {}
        self._wheeld_tasks = {}
        self.wheeld()
        self.wheeld_fin()
        super().__init__()

    @Daemon.daemon_main
    def wheeld(self):
        async def _main():
            print("bbbbbb")
            while True:
                print("waitttttttttt")
                queget = await self._wheeld_queue.get()
                print(queget)
                for i in self._wheeld_ope:
                    if queget[0] == i:
                        self._wheeld_tasks[i].append(asyncio.create_task(self._wheeld_ope[i](*queget[1:])))
                        break
                else:
                    if queget[0] == "break":
                        break
                    else:
                        print(f"Invalid operation:{queget[0]}")
            for i in self._wheeld_tasks:
                for r in self._wheeld_tasks[i]:
                    r.cancel()
                    try:
                        await r
                    except asyncio.CancelledError:
                        pass

        print("hununmo")
        asyncio.run(_main())

    def wheeld_ope_add(self, name, func):
        if self._wheeld_ope.get(name):
            raise KeyError(f"命令の名前:{name}:はもう登録されています")
        self._wheeld_ope[name] = func
        self._wheeld_tasks[name] = []
    
    def wheeld_ope_put(self, name, *arg):
        self._wheeld_queue.put_nowait((name, *arg))

    @Daemon.daemon_fin
    def wheeld_fin(self):
        print("aaaa")
        self.wheeld_ope_put("break")
        print("gnu")
        # self._mains[__class__.__name__].join()
        print(__class__.__name__)