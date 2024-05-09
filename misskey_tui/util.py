from unicodedata import east_asian_width


def check_terminal_haba(target: str) -> int:
    """ターミナル上での実際の幅を調べる"""
    length = 0
    for i in target:
        if east_asian_width(i) in "FWA":
            length += 2
        else:
            length += 1
    return length
