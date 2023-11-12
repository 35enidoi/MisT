def makeqr(url,width,height):
    """
    QRコードを作る関数

    optionalのqrcodeがあればQRコードを作る

    ただしスクリーンのサイズが小さいとそのまま"""
    try:
        import qrcode
        qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=1,
        border=3,
    )
        qr.add_data(url)
        qr.make()
        image = qr.make_image(fill_color="black", back_color="white")
        image.show()
        if (size := image.size[0]) > (width if width > height else height)//4:
            raise ImportError
        else:
            rttxt = ""
            for i in range(size):
                for r in range(size):
                    if image.getpixel((i,r)) == 255:
                        rttxt += "■"
                    else:
                        rttxt += "□"
                rttxt += "\n"
            return rttxt
    except ImportError:
        space = "      \n      "
        lens = width//2
        lines = len(url)//lens
        return space.split("\n")[0]+space.join([url[i*lens:(i+1)*lens] for i in range(lines)])

def webshow(url):
    """
    WEBを開く関数
    
    デスクトップ環境がない場合動作しないことを確認済み(Raspberry Pi OS Lite(Bullseye) : Raspberrypi Zero 2 W)(SSH接続)"""
    import webbrowser
    webbrowser.open(url)