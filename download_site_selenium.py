import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import shutil

# Google Sites URL (GitHub SecretsのGOOGLESITES_URLを使う)
GOOGLESITES_URL = os.getenv('GOOGLESITES_URL')

if GOOGLESITES_URL is None:
    raise ValueError('GOOGLESITES_URL is not set in environment variables')

# Chromeの設定
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # ヘッドレスモード
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')

# WebDriverのセットアップ
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# サイトのURLにアクセス
driver.get(GOOGLESITES_URL)
time.sleep(5)  # サイトが完全に読み込まれるまで待機

# ダウンロードするディレクトリを作成
download_dir = "downloaded_site"
if os.path.exists(download_dir):
    shutil.rmtree(download_dir)  # 既存のディレクトリを削除

os.makedirs(download_dir)

# 画像などのファイルを保存
# ページに埋め込まれた画像やファイルをダウンロードするコードを書く
# ここでは例として画像URLを取得している
images = driver.find_elements(By.TAG_NAME, "img")
for idx, img in enumerate(images):
    src = img.get_attribute("src")
    if src:
        image_name = os.path.join(download_dir, f"image_{idx}.jpg")
        with open(image_name, 'wb') as f:
            f.write(requests.get(src).content)

# 必要であれば、HTMLファイルも保存（ダウンロード）
html_content = driver.page_source
with open(os.path.join(download_dir, "index.html"), 'w', encoding='utf-8') as f:
    f.write(html_content)

driver.quit()
