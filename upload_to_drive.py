import os
import base64
import json
import requests
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

# 既存の site.zip ファイルを削除
results = drive_service.files().list(
    q=f"name='site.zip' and '{folder_id}' in parents",
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
# ここで "downloaded_site" の中身をZIP化
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

# ★ここでGitHubの最新リンクを更新します
# Google DriveのファイルIDを使ってダウンロードリンクを作成
file_id = uploaded_file.get('id')
download_link = f"https://drive.google.com/uc?export=download&id={file_id}"

# GitHubのアクセストークンとリポジトリ情報を設定
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
REPO_OWNER = "IRON-8470"  # リポジトリ所有者のユーザー名
REPO_NAME = "google-sites-server"  # リポジトリ名
FILE_PATH = "latest.txt"  # 更新するファイルのパス

# GitHub API URL
url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"

# 最新リンクの内容をJSONで準備
data = {
    "message": "Update latest download link",
    "content": base64.b64encode(download_link.encode("utf-8")).decode("utf-8"),
    "branch": "main"  # 適切なブランチ名を指定
}

# GitHub APIを使ってファイルを更新
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
}

# 既存のlatest.txtファイルのSHAを取得しておく
response = requests.get(url, headers=headers)
if response.status_code == 200:
    file_info = response.json()
    sha = file_info["sha"]
    data["sha"] = sha

    # ファイルを更新
    update_response = requests.put(url, json=data, headers=headers)
    if update_response.status_code == 200:
        print("latest.txtが更新されました。")
    else:
        print("ファイルの更新に失敗しました:", update_response.text)
else:
    print("ファイル情報の取得に失敗しました:", response.text)

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
