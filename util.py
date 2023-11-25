def pypcopy(url):
    """
    copyする奴"""
    try:
        import pyperclip
        pyperclip.copy(url)
        return True
    except (ImportError, pyperclip.PyperclipException):
        return False

def webshow(url):
    """
    WEBを開く関数
    
    デスクトップ環境がない場合動作しないことを確認済み(Raspberry Pi OS Lite(Bullseye) : Raspberrypi Zero 2 W)(SSH接続)"""
    import webbrowser
    webbrowser.open(url)

def mistfigleter():
    """
    'MisT'をFiglet化する関数"""
    from pyfiglet import figlet_format
    from random import randint
    fonts = ["binary","chunky","contessa","cybermedium","hex","eftifont","italic","mini","morse","short"]
    randomint = randint(0,len(fonts)+1)
    if randomint == len(fonts):
        mist_figs = "MisT\n"
    elif randomint == len(fonts)+1:
        mist_figs = """
MM     MM     TTTTTTTTTTT
M M   M M  I       T
M  M M  M  I  SSS  T
M   M   M     S    T
M       M  I  SSS  T
M       M  I    S  T
M       M  I  SSS  T """
    else:
        mist_figs = figlet_format("MisT",fonts[randomint])
    return mist_figs