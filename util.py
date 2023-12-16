def pypcopy(url):
    """
    copyする奴
    
    optionalのpyperclipがあればcopyする"""
    try:
        import pyperclip
        try:
            pyperclip.copy(url)
            return True
        except pyperclip.PyperclipException:
            return False
    except (ImportError):
        return False

def webshow(url):
    """
    WEBを開く関数"""
    import webbrowser
    try:
        browser = webbrowser.get()
        if type(browser) is webbrowser.GenericBrowser:
            return
        else:
            browser.open(url)
    except webbrowser.Error:
        return

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

if __name__ == "__main__":
    print("""
                          @#99999&&&&&&9##G2
                         999##9#GHG#9&@@@&&&999##H
                       @999GGh2AAssA23HG#99&@@@&&&&&&
                      &99#GG3s.       23hhhHHGG#9&&@#
                     @99GGGhs               r3hhHHGHA
                    &&9#GGhA                       A
                   @&9#GGhA
                 @@&9GGHh
                @&&9GGH3
               @&&#GGH3
              @@&#GGh2
             &@&#G#h2
            @&&#GGh2
          @@@9GGGh2
         &&@9G#Ghs
        &&&#G#Hh
       &&&#GGh2
      &&&#GGh2
     &&&#GGhA
   9&&9G#G2s
  #&@9G#H2;
 &&@9G#HA:
&&@9##hA
#GHG#hs
GHhH3A""")
    print("\nThis is hexagon-wrench.\n実行するファイル間違えてるよ!")