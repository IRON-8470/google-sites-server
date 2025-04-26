import os
import base64
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import zipfile

# GitHub Secretsからbase64エンコードされたcredentials.jsonの内容を取得
credentials_base64 = os.environ.get('GDRIVE_CREDENTIALS_JSON')
if credentials_base64 is None:
    raise ValueError('GDRIVE_CREDENTIALS_JSON not set in environment variables')

# base64デコードしてcredentials.jsonを生成
credentials_json = base64.b64decode(credentials_base64)

# credentials.jsonを読み込んで認証情報を取得
credentials = service_account.Credentials.from_service_account_info(
    json.loads(credentials_json), scopes=["https://www.googleapis.com/auth/drive"]
)

# Google Drive APIクライアントを作成
drive_service = build('drive', 'v3', credentials=credentials)

# GDRIVE_FOLDER_ID 環境変数からアップロード先フォルダIDを取得
folder_id = os.environ.get('GDRIVE_FOLDER_ID')
if folder_id is None:
    raise ValueError('GDRIVE_FOLDER_ID not set in environment variables')

# 既存の site.zip ファイルがあれば削除
if os.path.exists('site.zip'):
    os.remove('site.zip')
    print("古い site.zip を削除しました")

# ダウンロードしたサイトをZIP化
# ここで "downloaded_site" の中身をZIP化
if not os.path.exists('downloaded_site'):
    raise ValueError('ダウンロードしたサイトのディレクトリが見つかりません')

with zipfile.ZipFile('site.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk('downloaded_site'):
        for file in files:
            zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), 'downloaded_site'))

current_directory = os.getcwd()  # 現在の作業ディレクトリ
zip_files = [f for f in os.listdir(current_directory) if f.endswith('.zip')]  # ZIPファイルのみをフィルタ

if zip_files:
    print("フォルダー内のZIPファイル:")
    for zip_file in zip_files:
        print(zip_file)  # 各ZIPファイルの名前を表示
else:
     print("ZIPファイルはフォルダーにありません")

# アップロード処理（フォルダを指定）
file_metadata = {
    'name': 'site.zip',
    'parents': [folder_id]
}
media = MediaFileUpload('site.zip', mimetype='application/zip')
uploaded_file = drive_service.files().create(
    body=file_metadata,
    media_body=media,
    fields='id, webViewLink'
).execute()

# アップロード成功メッセージとファイル情報の表示
print("アップロード成功")
print("ファイルID:", uploaded_file.get('id'))
print("アクセスURL:", uploaded_file.get('webViewLink'))

# リンクを知っている全員に公開設定
drive_service.permissions().create(
    fileId=uploaded_file.get('id'),
    body={
        "type": "anyone",
        "role": "reader"
    },
    fields="id"
).execute()

# 公開設定完了メッセージ
print("リンクを知っている全員に公開設定しました")
