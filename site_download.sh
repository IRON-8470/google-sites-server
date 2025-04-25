#!/bin/bash

# Google SitesのURL
SITES_URL="https://sites.google.com/your-site-url"

# ダウンロード先ディレクトリとファイル名
DOWNLOAD_DIR="site"
ZIP_FILE="site.zip"

# Google Sitesのページをwgetでダウンロード
wget -r -l inf -nd -np -P $DOWNLOAD_DIR $SITES_URL

# ダウンロードしたファイルをZIPに圧縮
zip -r $ZIP_FILE $DOWNLOAD_DIR
