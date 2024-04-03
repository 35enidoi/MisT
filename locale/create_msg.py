# coding=utf-8

# potファイルからpoファイルとmoファイルをCUIで上書き及び更新できるやーつ
# gettext_fromtextenum.pyと同じくpolibが必要
import polib
from os import path as os_path
from os import mkdir
from datetime import datetime

# from pprint import pprint

def diff_chacker(bef:dict, aft:dict) -> dict:
    diff = {}
    diff["add"] = {i:v for i, v in aft.items() if i not in bef}
    diff["delete"] = {i:v for i, v in bef.items() if i not in aft}
    # key:"befval -> aftval"
    diff["change"] = {i:f"{bef[i]} -> {v}" for i, v in aft.items() if i in bef and v != bef[i]}
    return diff

def get_path(target_name:str) -> str:
    """相対パスから絶対パス作る奴"""
    return os_path.abspath(os_path.join(os_path.dirname(__file__),target_name))

print("potファイル読み込み...")
pot = polib.pofile(get_path("messages.pot"), encoding="utf-8")
name = str(input("名前を入力してください "))
langname = str(input("作りたい言語ファイルの名前を入力してください\n例:ja_JP "))
print("言語ファイルがあるか検出...")
if os_path.isdir(get_path(langname)):
    print("言語ファイルを読み込み...")
    po = polib.pofile(get_path(langname+"/LC_MESSAGES/messages.po"), encoding="utf-8")
    if po.metadata["Last-Translator"] != name:
        print("翻訳者の違いを検出！\n{} -> {}".format(po.metadata["Last-Translator"], name))
        if input("翻訳者を変更しますか？前の翻訳者に確認をとってからお願いします。(Y/else) ").lower() not in ("y", "yes"):
            print("中止...")
            exit()
    print("メタデータのコピーと変更...")
    po.metadata = pot.metadata.copy()
    po.metadata["Last-Translator"] = name
else:
    print("言語ファイル無いのでディレクトリ作成...")
    mkdir(get_path(langname))
    mkdir(get_path(langname+"/LC_MESSAGES"))
    print("新規にpotファイルから作成...")
    po = polib.POFile(encoding="utf-8")
    print("ヘッダーのコピー...")
    po.header = pot.header
    print("メタデータのコピーと変更...")
    po.metadata = pot.metadata.copy()
    po.metadata["Last-Translator"] = name

diff = diff_chacker({i.msgid:i.msgstr for i in po}, {i.msgid:i.msgstr for i in pot})
if diff["delete"] != {}:
    print("potファイル内にない以下のidを削除します:\n"+"\n".join(map(repr, diff["delete"].keys()))+"\n\n")
    for i in diff["delete"].keys():
        po.pop([r.msgid for r in po].index(i))
if diff["add"] != {}:
    print("翻訳できる文字を検出！\n翻訳作業に入ります...")
    for i in reversed(range(len(diff["add"]))):
        print(f"\n残り:{i+1}")
        print(f"参照変数名:{','.join((pot[[r.msgid for r in pot].index(tuple(diff['add'].keys())[i])].flags))}")
        print(f"msgid:{repr(tuple(diff['add'].keys())[i])[:]}")
        while True:
            msgstr = str(input("msgstr:"))
            if msgstr.count("{}") == tuple(diff["add"].keys())[i].count("{}"):
                break
            else:
                print("`{}`の数があっていません。もう一度入力してください。")
        po.append(polib.POEntry(msgid=tuple(diff["add"].keys())[i], msgstr=msgstr))
print("フラッグをpotファイルからコピー...")
po.sort()
pot.sort()
for i in range(len(po)):
    po[i].flags = pot[i].flags.copy()
print("作成日を挿入...")
po.metadata["PO-Revision-Date"] = datetime.now().astimezone()
print("poファイルを作成...")
po.save(get_path("./"+langname+"/LC_MESSAGES/messages.po"))
print("moファイルを作成...")
po.save_as_mofile(get_path("./"+langname+"/LC_MESSAGES/messages.mo"))