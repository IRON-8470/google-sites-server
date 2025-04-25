import os
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 認証情報とサービスをセットアップ
creds, project = google.auth.load_credentials_from_file('credentials.json')
drive_service = build('drive', 'v3', credentials=creds)

# アップロードするファイルのパス
file_name = 'site.zip'
file_path = os.path.join(os.getcwd(), file_name)

# Driveにアップロードする
file_metadata = {'name': file_name, 'parents': ['your-folder-id']}
media = MediaFileUpload(file_path, mimetype='application/zip')

# ファイルをDriveにアップロード
uploaded_file = drive_service.files().create(
    media_body=media, body=file_metadata, fields='id'
).execute()

# アップロードしたファイルのIDを取得
file_id = uploaded_file['id']

# ファイルIDを保存（GitHub Actionsで利用）
with open('latest_file_id.txt', 'w') as f:
    f.write(file_id)

print(f"Uploaded file ID: {file_id}")
