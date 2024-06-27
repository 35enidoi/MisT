from unicodedata import east_asian_width
import webbrowser


def check_terminal_haba(target: str) -> int:
    """ターミナル上での実際の幅を調べる"""
    length = 0
    for i in target:
        if east_asian_width(i) in "FWA":
            length += 2
        else:
            length += 1
    return length


def web_show(url: str) -> None:
    """WEBを開く関数"""
    try:
        browser = webbrowser.get()
        if type(browser) is webbrowser.GenericBrowser:
            return
        else:
            browser.open(url)
    except webbrowser.Error:
        return
