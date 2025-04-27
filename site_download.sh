#!/bin/bash

# Google SitesのURL
SITES_URL="https://sites.google.com/view/niyariiko-ru/home"

# ダウンロード先ディレクトリとファイル名
DOWNLOAD_DIR="downloaded_site"
ZIP_FILE="site.zip"

# 古いダウンロードディレクトリを削除
rm -rf $DOWNLOAD_DIR

# Google Sitesのページをwgetでダウンロード
wget \
    --recursive \            # リンクをたどって再帰的にダウンロード
    --page-requisites \      # 画像やCSS、JSも取得
    --html-extension \       # HTMLは拡張子を.htmlにする
    --convert-links \        # ローカル用にリンク書き換え
    --no-parent \            # 親ディレクトリに行かない
    --header="Cache-Control: no-cache" \
    --directory-prefix=$DOWNLOAD_DIR \  # 保存先
    "$SITES_URL"

# ダウンロードしたファイルをZIPに圧縮
rm -f $ZIP_FILE
zip -r $ZIP_FILE $DOWNLOAD_DIR
