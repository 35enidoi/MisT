def shorter(url,width):
    """画面に合わせて改行を入れるもの"""
    space = "      \n      "
    lens = width//2
    lines = len(url)//lens
    return space.split("\n")[0]+space.join([url[i*lens:(i+1)*lens] for i in range(lines)])

def pypcopy(url):
    """
    copyする奴"""
    try:
        import pyperclip
        pyperclip.copy(url)
        return True
    except ImportError:
        return False

def webshow(url):
    """
    WEBを開く関数
    
    デスクトップ環境がない場合動作しないことを確認済み(Raspberry Pi OS Lite(Bullseye) : Raspberrypi Zero 2 W)(SSH接続)"""
    import webbrowser
    webbrowser.open(url)