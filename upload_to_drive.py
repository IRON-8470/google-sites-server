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

# Google Drive内の既存のsite.zipファイルを検索して削除
results = drive_service.files().list(
    q=f"name = 'site.zip' and '{folder_id}' in parents",  # 同じ名前のファイルを検索
    fields="files(id, name)"
).execute()

files = results.get('files', [])

for file in files:
    file_id = file['id']
    file_name = file['name']
    print(f"削除予定: {file_name} (ID: {file_id})")
    drive_service.files().delete(fileId=file_id).execute()  # ファイルを削除

print("古い site.zip を削除しました")

# ダウンロードしたサイトをZIP化
if not os.path.exists('downloaded_site'):
    raise ValueError('ダウンロードしたサイトのディレクトリが見つかりません')

with zipfile.ZipFile('site.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk('downloaded_site'):
        for file in files:
            zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), 'downloaded_site'))

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

# 最新のzipファイルへの直リンクを生成
file_id = uploaded_file.get('id')
download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

# latest.txtを更新
latest_txt_metadata = {
    'name': 'latest.txt',
    'parents': [folder_id]
}

# 最新URLをlatest.txtに書き込み
with open('latest.txt', 'w') as f:
    f.write(download_url)

# latest.txtをGoogle Driveにアップロード
media = MediaFileUpload('latest.txt', mimetype='text/plain')
drive_service.files().create(
    body=latest_txt_metadata,
    media_body=media
).execute()

print("latest.txtを更新しました。")
