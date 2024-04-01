# MisT
![image](https://github.com/35enidoi/MisT/assets/143810964/136e0fda-cdbf-4cdc-8082-b1470b9cfc4b)

英語が読めない？日本語も難しい？  
そんなあなたに朗報！！！！  
なんと4月1日のv0.41アップデートにより、MisTはASCIIコード(ord関数を使ってるので正確にはUnicode)に対応！！！！  
数字だけなので9個の文字`1,2,3,4,5,6,7,8,9`を覚えれば、安心！！！🤯🤯🤯  

...ということでエイプリルフールです  
なお、実際のところordで変換しただけなので英単語の意味を知る必要がある模様。  
さらにまだ翻訳が行き届いてないところもある模様。

翻訳に使用したファイルは [これです](locale/create_en_ascii_langfile.py)  
自作しました。`polib`というライブラリが必要なので注意

<details>

<summary>言語選択のしかた</summary>

![image](https://github.com/35enidoi/MisT/assets/143810964/8629f176-9ced-4de5-926d-4ab27f5c4e43)
1. 一番右の`Config`を選択
![image](https://github.com/35enidoi/MisT/assets/143810964/19b74522-4209-4205-93bf-3d3e53cca65f)
2. `Language`を選択
![image](https://github.com/35enidoi/MisT/assets/143810964/d8c0375b-66af-4c98-b220-804297fdb29f)
3. このようなポップアップが出てくるので、en_ASCIIを選択
4. 完了

</details>



[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2F35enidoi%2FMisT.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2F35enidoi%2FMisT?ref=badge_shield)
## 説明  
テキストユーザーインターフェース(TUI)のMisskeyクライアントです  
まだ開発中なので機能は少ないしバグもあるかもしれません。  
### なぜTUI？  
CUIだと操作が難しいけどGUIだとデスクトップ環境(あとマウスも)が必要だからです  
要は**かっこいいから**です。  
## 作った理由  
- デスクトップ環境のないパソコンでMisskeyしたい
- TUIがかっこいい
- 学習
## 特徴
- 軽い
- デスクトップ環境がなくても使える
- キーボードだけで操作できる
- CUIみたいでかっこいい
- GUIのような操作感
## 問題  
ASCIIMATICSの仕様上windowsでは表示が崩れる可能性が高いです。  
`chcp 65001`をしてから実行してください  
詳細は[こちら](https://asciimatics.readthedocs.io/en/stable/troubleshooting.html#id2)
## 使ってるライブラリ  
[ASCIIMATICS](https://github.com/peterbrittain/asciimatics)と[misskey.py](https://github.com/YuzuRyo61/Misskey.py)を使っています
## License  
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2F35enidoi%2FMisT.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2F35enidoi%2FMisT?ref=badge_large)
