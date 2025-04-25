# google-sites-server
## Google SitesをGoogle Driveへ自動的にアップロード

## 概要
- このプロジェクトは、Google Sitesのページを定期的にダウンロードし、ZIP化してGoogle Driveにアップロードします。
- 最新のZIPファイルのダウンロードリンクは、GitHub Pagesを使って公開されます。

## 設定方法
1. `credentials.json` をGoogle Cloud Consoleから取得し、プロジェクトのルートディレクトリに配置。
2. GitHub ActionsのSecretsに以下の情報を設定:
   - `GDRIVE_FOLDER_ID`：アップロード先のGoogle DriveフォルダID
   - `GDRIVE_CREDENTIALS_JSON`：`credentials.json`の内容をBase64でエンコードしたもの
3. `.github/workflows/upload.yml` は自動でGoogle Driveにアップロードを実行します。
4. 最新のダウンロードリンクは `https://yourusername.github.io/latest.txt` からアクセス可能です。
