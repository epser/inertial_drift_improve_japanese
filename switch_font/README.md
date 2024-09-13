# LocalizedFont変更

## ファイル群

- uabea_asset_dump/
  - SubheadingsAlphabet-resources.assets-100001.txt - LocalizedFont型のMonoBehavior(copy from Subheadings-resources.assets-34629)、日本語の参照フォントを英語版に変更している
  - TextLocaliser-level1-37059.txt - "LOADING ...." とフォントを紐づけるMonoBehavior
  - TextLocaliser-level1-38842.txt - "LOADING ...." とフォントを紐づけるMonoBehavior

## 適用手順

1. UABEAでresources.assetsとlevel1を開く
2. 親ウィンドウからType114(MonoBehavior)をresources.assetsに新規作成する
3. 各ファイルを対象行に向けてインポート
