# 翻訳を作成するには

## メインプログラムから翻訳したい文字列を抽出

* まずはメインプログラムで翻訳したい文字列の前後を _ でマーキングする。例: "translate me!" を　(_("translate me!") のようにマーキング。その後、pygettextで翻訳したい文字列をメインプログラムから抽出する。

```
python pygettext.py -d messages -p ../locale/ ../misskey_tui.py
```

* このときメインプログラムのすべてのf文字列はf'Hey {username},' から (_('Hey {},').format(username)の形式に変更しなければならない。


## 翻訳作業

* その後生成されたmessages.potを目的の言語フォルダにコピーしてmsgstrに対応する翻訳を記入。この際に.potファイルを拡張子.poに変更する。

```
cp messages.pot ja_JP/LC_MESSAGES/messages.po
```

## 翻訳した文字列をコンパイル

* 記入し終わったら、最後に目的言語のmessages.poを以下のコマンドでコンパイルして動作確認をする。

```
python msgfmt.py ./ja_JP/LC_MESSAGES/messages.po
```

# 参考情報

* [Qiita](https://qiita.com/Tadahiro_Yamamura/items/147daed0a6fcea32a481)