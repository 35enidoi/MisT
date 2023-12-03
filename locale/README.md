#　翻訳を作成するには

*まずはメインプログラムで翻訳したい文字列の前後を _ でマーキングする。例: "translate me!" を　(_("translate me!") のようにマーキング。その後、pygettextで翻訳したい文字列をメインプログラムから抽出する。

```
python pygettext.py -d messages -p ../locale/ ../misskey_tui.py/ 
```

*その後生成されたmessages.potを目的の言語フォルダにコピーしてmsgstrに対応する翻訳を記入。この際に.potファイルを拡張子.poに変更する。

```
cp messages.pot ja_JP/LC_MESSAGES/messages.po
```

*記入し終わったら、最後に目的言語のmessages.poを以下のコマンドでコンパイルして動作確認をする。

```
python msgfmt.py /ja_JP/LC_MESSAGES/messages.po
```