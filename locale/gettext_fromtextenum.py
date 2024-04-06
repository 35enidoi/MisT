# coding=utf-8

# textenumからgettextしてくるやーつ
# 重要:textenumとmessages.potがある前提のスクリプトです。
#      polibというライブラリが必要です。

SCRIPT_VERSION = "1.0"

from collections import defaultdict
from datetime import datetime
from os import path as os_path
import polib

# # デバッグ用のpprintのimport
# from pprint import pprint

def get_path(target_name:str) -> str:
    """相対パスから絶対パス作る奴"""
    return os_path.abspath(os_path.join(os_path.dirname(__file__),target_name))

# textenumsをimportする前準備(パスを通す)
from sys import path as sys_path
sys_path.append(get_path("../"))
# textenumsをimport
import textenums
# バージョン確認のため、本体からMkAPIsをimport
from misskey_tui import MkAPIs

def diff_chacker(bef:dict, aft:dict) -> dict:
    diff = {}
    diff["add"] = {i:v for i, v in aft.items() if i not in bef}
    diff["delete"] = {i:v for i, v in bef.items() if i not in aft}
    # key:"befval -> aftval"
    diff["change"] = {i:f"{bef[i]} -> {v}" for i, v in aft.items() if i in bef and v != bef[i]}
    return diff

def diff_keikoku(place:str, diff:dict) -> bool:
    printtext = "{}が変更されます！！！！！！！\n下が変更するとこ\n\n{}\n"
    printtext = printtext.format(place, "\n\n".join(map(lambda i:"{}:\n{}".format(i[0], "\n".join(map(lambda x:f"{repr(x[0])} : {repr(x[1]) if x[1] != '' else None}", i[1].items())) if len(i[1]) > 0 and i[1] is not str else None), diff.items())))
    return input(printtext+"\n変更しますか?(Y/else) ").lower() in ("yes", "y")


print("既存のpotファイルを読み込み...")
bef_pot = polib.pofile(get_path("./messages.pot"), encofing="utf-8")

print("新しいpotを作成...")
aft_pot = polib.POFile()

print("metadeta等をコピー...")
aft_pot.metadata = bef_pot.metadata.copy()
aft_pot.header = bef_pot.header

print("metadetaを変更...")
if bef_pot.metadata["Generated-By"] != os_path.basename(__file__) + " " + SCRIPT_VERSION:
    aft_pot.metadata["Generated-By"] = os_path.basename(__file__) + " " + SCRIPT_VERSION
if bef_pot.metadata["Project-Id-Version"] != "MisT " + str(MkAPIs.version):
    aft_pot.metadata["Project-Id-Version"] = "MisT " + str(MkAPIs.version)
aft_pot.metadata["POT-Creation-Date"] = datetime.now().astimezone()

# メタデータの変更点を警告
diff = diff_chacker(bef_pot.metadata, aft_pot.metadata)
if any(map(lambda x:x != {}, diff.values())):
    if not diff_keikoku("メタデータ", diff):
        print("中止します...")
        exit()

print("翻訳文字を検出...")
targets = defaultdict(list)
for enums in (getattr(textenums, s) for s in textenums.__all__):
    for enum in enums:
        targets[enum._value_].append(enums.__name__+"."+enum.name)
print("検出した翻訳文字をpotに挿入...")
for i, v in targets.items():
    aft_pot.append(polib.POEntry(msgid=i, msgstr="", flags=v))

diff = diff_chacker({i.msgid:i.msgstr for i in bef_pot}, {i.msgid:i.msgstr for i in aft_pot})
if any(map(lambda x:x != {}, diff.values())):
    if not diff_keikoku("テキスト", diff):
        print("中止します...")
        exit()

print("新しいpotで上書き...")
aft_pot.save(get_path("./messages.pot"))