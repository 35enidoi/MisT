# 翻訳を作成するには

> [!WARNING]  
polibというライブラリが必要です。

## メインプログラムから翻訳したい文字列を別ファイルに移動

1. まず、メインプログラムで翻訳する文字のあるシーン別に`textenum`ディレクトリに`<scenename>_txts.py`として作成。  
    1. 別に`<scenename>_txts.py`として作らなくても名前は適当で大丈夫ですが、その方が統一感あるのでできるだけそうしてください。

2. 次に、そのpythonプログラム内にクラスを作成。
    1. 名前は何でもよいですが、シーンの名前がわかりやすい、それでいて少ない文字列にした方が良いです。例えば、`CreateNote`シーンであれば`CN_T`です。
    2. このクラスには`Enum`を継承させてください。
    3. また、下の関数をクラス内に**必ず**作ってください。(コピーすればよいです。)
    ```py
    def __getattribute__(self, __name: str) -> Any:
        if __name == "value":
            return _(super().__getattribute__(__name))
        return super().__getattribute__(__name)
    ```
    4. `textenums/__init__.py`にこのクラスを`import`する文を追加してください。じゃないと使えません。

3. 翻訳する文字を変数としてこのクラス内に置いていく
    1. 翻訳する文字を`Enum`として使うからです。
    2. 例:
    ```
    HONI = "honi"
    ```

4. 文字をこのクラスから変数を通して`.value`で受け取る
    1. **絶対**に`.value`を付けて受け取ってください。動きません。
    2. 例:(翻訳対象の文字をクラス`EXAMPLE_T`に`HONYAKU_TXT`として変数を定義した場合)  
    ```
    EXAMPLE_T.HONYAKU_TXT.value
    ```

## potファイル更新
この`README.md`のあるファイル`locale`内にあるスクリプト`gettext_fromtextenum.py`を用いる。  

使い方は簡単。
```
python gettext_fromtextenum.py
```
これを実行するだけ。  

あとは変更点が表示されるので確認しながら`yes`あるいは`y`と入力してれば`messages.pot`が更新される。

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