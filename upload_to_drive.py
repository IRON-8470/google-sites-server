import os
import base64
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

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

# アップロード処理（例）
file_metadata = {'name': 'site.zip'}
media = MediaFileUpload('site.zip', mimetype='application/zip')
file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

print(f'File ID: {file["id"]}')
