from functools import partial
import asyncio
import threading

class Daemon:
    """悪魔クラス"""

    d_dict = {"_cls":None}

    def __init__(self, cls:type) -> None:
        self.d_dict["_cls"] = cls
        super().__init__()

    def _startds(self):
        "悪魔の召喚"
        dmains = {"returns":[], "mains":{}}
        clss = {}
        for i in self.d_dict:
            if type(val := self.d_dict[i]) == dict:
                clss[i] = val

        async def _main(fineve_:asyncio.Event, starteve_:asyncio.Event, clss_:dict, mains_:dict):
            for i in clss_:
                mains_["mains"][i] = asyncio.create_task(clss_[i]["main"][0](*clss_[i]["main"][1:]))
            starteve_.set()
            await asyncio.to_thread(fineve_.wait)
            n = 0
            for i in mains_["mains"]:
                if clss_[i].get("fin"):
                    if mains_["fins"][n]:
                        pass
                    else:
                        mains_["mains"][i].cancel()
                    n += 1
                else:
                    mains_["mains"][i].cancel()
                try:
                    await mains_["mains"][i]
                except asyncio.CancelledError:
                    pass

        async def _fin(fineve_:asyncio.Event, th_:threading.Thread, clss_:dict[dict], mains_:dict):
            mains_["fins"] = await asyncio.gather(*(clss_[i]["fin"][0](*clss_[i]["fin"][1:]) for i in clss_ if clss_[i].get("fin")))
            fineve_.set()
            th_.join()

        starteve = threading.Event()
        fineve = threading.Event()
        th = threading.Thread(target=lambda:asyncio.run(_main(fineve, starteve, clss, dmains)))
        th.start()
        starteve.wait()
        return lambda:asyncio.run(_fin(fineve, th, clss, dmains))

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
                if asyncio.iscoroutinefunction(func):
                    self.d_dict[clsname]["main"] = (func, *args)
                else:
                    raise ValueError(f"メイン関数はコルーチンでなければなりません。")
            else:
                raise KeyError(f"クラス:{clsname} は未登録です。")
        return _wrap

    @classmethod
    def daemon_fin(self, func):
        """
        悪魔の終了処理を入れる場所

        ラッピングした後に実行することで予約される
        
        予約する関数の返り値をTrueにすることでそのクラスのメイン関数をキャンセルせずにawaitさせるようにする"""
        def _wrap(*args):
            if self._check_deamonname(self, clsname:=func.__qualname__.split(".")[-2]):
                if asyncio.iscoroutinefunction(func):
                    self.d_dict[clsname]["fin"] = (func, *args)
                else:
                    raise ValueError(f"終了処理関数はコルーチンでなければなりません。")
            else:
                raise KeyError(f"クラス:{clsname} は未登録です。")
        return _wrap

    @classmethod
    def glb_getter(self, func):
        """
        MkAPIsのクラスを第一因数に持ってくるようにするラッパー

        MkAPIsの関数や変数を使いたい場合に使う"""
        return partial(func, self.d_dict["_cls"])