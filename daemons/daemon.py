from functools import partial
import asyncio
import threading

class Daemon:
    """悪魔クラス"""

    d_dict = {}
    _d_cls = {"cls":None}

    def __init__(self, cls:type, cfg:dict) -> None:
        """
        cls:MkAPIs
        cfg:mistconfig"""
        self._d_cls["cls"] = cls
        self._d_cls["cfg"] = cfg
        super().__init__()

    def _startds(self):
        "悪魔の召喚"
        async def _main(fineve_:asyncio.Event, starteve_:asyncio.Event, d_dict_:dict, mains_:dict):
            for i in d_dict_:
                mains_["mains"][i] = asyncio.create_task(d_dict_[i]["main"][0](*d_dict_[i]["main"][1:]))
            starteve_.set()
            await asyncio.to_thread(fineve_.wait)
            n = 0
            for i in mains_["mains"]:
                if d_dict_[i].get("fin"):
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

        async def _fin(fineve_:asyncio.Event, th_:threading.Thread, d_dict_:dict[dict], mains_:dict):
            mains_["fins"] = await asyncio.gather(*(d_dict_[i]["fin"][0](*d_dict_[i]["fin"][1:]) for i in d_dict_ if d_dict_[i].get("fin")))
            fineve_.set()
            th_.join()

        dmains = {"returns":[], "mains":{}}
        starteve = threading.Event()
        fineve = threading.Event()
        th = threading.Thread(target=lambda:asyncio.run(_main(fineve, starteve, self.d_dict, dmains)))
        th.start()
        starteve.wait()
        return lambda:asyncio.run(_fin(fineve, th, self.d_dict, dmains))

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

        ラッピングした後に実行することで予約される
        
        ラッピングする関数はコルーチンでなければならない"""
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
        
        ラッピングする関数はコルーチンでなければならない

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
        return partial(func, self._d_cls["cls"])