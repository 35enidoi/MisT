class Daemon:
    """悪魔クラス"""

    d_dict = {"_cls":None}

    def __init__(self, cls:type) -> None:
        self.d_dict["_cls"] = cls
        super().__init__()

    def _startds(self):
        "悪魔の召喚"
        import threading
        self._mains = {}
        for i in self.d_dict:
            if type(val := self.d_dict[i]) == dict:
                if val.get("main"):
                    print(f"runner added args {val['main'][1:]}")
                    runner = threading.Thread(target=val["main"][0], args=val["main"][1:], daemon=True)
                    runner.start()
                    self._mains[i] = runner
        print("added")

    def _finds(self):
        "悪魔の終了"
        fins = []
        for i in self.d_dict.values():
            if type(i) == dict:
                if i.get("fin"):
                    fins.append(i["fin"])
        if len(fins) > 0:
            import asyncio
            async def _execution(_fins):
                runners = []
                loop = asyncio.get_event_loop()
                for i in _fins:
                    if asyncio.iscoroutinefunction(i[0]):
                        runners.append(asyncio.create_task(i[0](*i[1:])))
                    else:
                        runners.append(loop.run_in_executor(None, i[0], *i[1:]))
                for i in runners:
                    await i
            asyncio.run(_execution(fins))

    def _check_deamonname(self, name) -> bool:
        if name in self.d_dict:
            return True
        else:
            return False

    @classmethod
    def newd(self, cls:type):
        """
        新しい悪魔を作るもの

        同じクラスがすでに存在する場合エラー"""
        if self._check_deamonname(self, cls.__name__):
            raise KeyError(f"クラス:{cls.__name__} はすでに登録済みです。")
        self.d_dict[cls.__name__] = {}
        return cls

    @classmethod
    def daemon_main(self, func):
        """
        悪魔の処理を入れる場所

        ラッピングした後に実行することで予約される"""
        def _wrap(*args):
            if self._check_deamonname(self, clsname:=func.__qualname__.split(".")[-2]):
                self.d_dict[clsname]["main"] = (func, *args)
            else:
                raise KeyError(f"クラス:{clsname} は未登録です。")
        return _wrap

    @classmethod
    def daemon_fin(self, func):
        """
        悪魔の終了処理を入れる場所

        ラッピングした後に実行することで予約される"""
        def _wrap(*args):
            if self._check_deamonname(self, clsname:=func.__qualname__.split(".")[-2]):
                self.d_dict[clsname]["fin"] = (func, *args)
            else:
                raise KeyError(f"クラス:{clsname} は未登録です。")
        return _wrap
    
    @classmethod
    def glb_getter(self, func):
        """
        MkAPIsのクラスを第一因数に持ってくるようにするラッパー

        MkAPIsの関数や変数を使いたい場合に使う"""
        def _wrap(*args):
            return func(self.d_dict["_cls"], *args)
        return _wrap