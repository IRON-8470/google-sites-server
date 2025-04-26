import os
import base64
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

print("GDRIVE_FOLDER_ID:", os.environ.get('GDRIVE_FOLDER_ID'))

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

print("アップロード成功")
print("ファイルID:", uploaded_file.get('id'))
print("アクセスURL:", uploaded_file.get('webViewLink'))

# ★ここを追加する（B案）
# リンクを知っている全員に公開設定
drive_service.permissions().create(
    fileId=uploaded_file.get('id'),
    body={
        "type": "anyone",
        "role": "reader"
    },
    fields="id"
).execute()

print("リンクを知っている全員に公開設定しました")

# (3) Drive内の最近のファイル一覧を表示（デバッグ用）
results = drive_service.files().list(
    pageSize=5,
    orderBy="createdTime desc",
    fields="files(id, name, webViewLink)"
).execute()

items = results.get('files', [])
print("Drive上のファイル一覧（直近5件）:")
for item in items:
    print(f"{item['name']} - {item['webViewLink']}")
