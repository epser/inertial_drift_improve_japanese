# 使用法: python json_overwrite.py [mode] arg1 arg2
# 
# ステップ:
#   1. UABE Avaloniaで、
#      resources.assets, sharedassets1.assets, sharedassets2.assets, sharedassets3.assets, sharedassets4.assets
#      を開く
#   2. FilterでMonoBehaviourだけを選んだ後、全選択してExport Dumpする
#   3. 出力されたファイル群から、Languageリソースを含まないファイルをどうにかして退避する
#   4. このスクリプトの -r オプションでダンプのディレクトリを指定し、TSVを書き出す
#   5. TSVを適当に翻訳・加工した後、このスクリプトの -w オプションでTSVを読み込み、jsonファイルを書き換える。-rと-wでTSVの形式が全く異なるので注意
#   6. UABE Avaloniaで再度リソースファイルを開き、jsonファイルをImport Dumpする

import re
import sys
import json
import os

# jsonファイルを読み込む
def load_json_file(file_path:str):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

# jsonファイルを書き込む
def write_json_file(file_path:str, data:dict):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# 改行とタブをエスケープする
def escape_string(string:str):
    if string is None:
        return ""
    return string.replace("\r\n", "\\n").replace("\n", "\\n").replace("\t", "\\t")

# 改行とタブをアンエスケープする
def unescape_string(string:str):
    if string is None:
        return ""
    return string.replace("\\n", "\n").replace("\\t", "\t")

# _strings.Array[] を検索し、Languageキーの値が引数と一致した場合にそのDataキーの値を返す
def search_language(json_data:dict, language:int):
    for item in json_data['_strings']['Array']:
        if item['Language'] == language:
            return item['Data']
    return None

# _strings.Array[] を検索し、Languageキーの値が引数2と一致した場合に引数1をDataキーの値に上書きしたdictを返す。一致しない場合は末尾に追加する
def overwrite_language(json_data:dict, language:int, data:str):
    for item in json_data['_strings']['Array']:
        if item['Language'] == language:
            item['Data'] = data
            return json_data
    json_data['_strings']['Array'].append({'Language': language, 'Data': data})
    return json_data

# ファイル名を引数に取って中身を出力
def print_file_information(file_path:str):
    json_data = load_json_file(file_path)

    file_name = os.path.basename(file_path)
    # file_nameを . か - で分割し、最後の要素はpopで破壊的に取り出す
    regex = re.compile(r'[.-]')
    split_file_name = regex.split(file_name)
    split_file_name.pop() # 最後の要素は削除
    path_id = split_file_name.pop() # 最後から2番目の要素はPathID

    # file_name を - で分割し、うしろから2番目の要素はcontainer_file_name
    hifen_split_file_name = file_name.split('-')
    container_file_name = hifen_split_file_name[-2]

    # json_data内の幾つかのキーを取り出して配列に収める
    arr = [
        json_data['Identifier'],
        file_name,
        json_data['m_Name'],
        json_data['Description'],
        container_file_name,
        path_id,
        json_data['Used'],
        escape_string(search_language(json_data, 1)),
        escape_string(search_language(json_data, 6)),
    ]
    # 配列をタブ区切りで出力
    print("\t".join(map(str, arr)))

# ファイル名と書き込み文字列を引数に取って内容を更新
def overwrite_file_information(file_path:str, language:int, data:str, dry_run:bool=False):
    json_data = load_json_file(file_path)
    json_data = overwrite_language(json_data, language, unescape_string(data))
    if not dry_run:
        write_json_file(file_path, json_data)

if __name__ == '__main__':
    # 引数が足りない場合はヘルプを表示
    if len(sys.argv) < 2:
        print("Usage: python json_overwrite.py [option] [file_path]")
        print("Options:")
        print("  -r [directory_path] : Output information of all files under the specified directory.")
        print("  -w [tsv_path] [directory_path]: Overwrite the json file with the contents of the TSV file.")
        print("  --dry-run [tsv_path] [directory_path]: Pseudo overwrite the json file with the contents of the TSV file.")
        sys.exit(1)

    options = {
        'read': '-r',
        'write': '-w',
        'dry_run': '--dry-run',
    }

    # -r オプションでディレクトリ書き出しモード。指定ディレクトリ配下の全ファイルの情報を出力
    if len(sys.argv) == 3 and sys.argv[1] == options['read']:
        dir_path = sys.argv[2]
        for file_name in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file_name)
            print_file_information(file_path)
        sys.exit(1)

    # -w/--dry-run オプションでディレクトリマージ。TSV、ディレクトリの順で引数を取り、TSVファイルの内容でjsonファイルを上書き。
    # TSVのフォーマットは "identifier", "file_name", "Data(Language=6)"
    if len(sys.argv) == 4 and (sys.argv[1] == options['write'] or sys.argv[1] == options['dry_run']):
        [tsv_path, dir_path] = sys.argv[2:]
        with open(tsv_path, 'r', encoding='utf-8') as file:
            # TSVの1行目はヘッダーなのでスキップ
            file.readline()
            for line in file:
                tsv_data = line.strip().split("\t")
                if len(tsv_data) < 3 or tsv_data[2] == "":
                    continue
                write_path = os.path.join(dir_path, tsv_data[1])
                print(write_path + " : " + tsv_data[2])
                # dry runの場合はファイルを書き換えない
                if sys.argv[1] == options['dry_run']:
                    overwrite_file_information(write_path, 6, tsv_data[2], True)
                else:
                    overwrite_file_information(write_path, 6, tsv_data[2])
        sys.exit(0)
