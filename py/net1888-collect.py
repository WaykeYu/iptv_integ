import os
import subprocess
import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# 設定 GitHub 倉庫路徑
GITHUB_REPO_URL = "git@github.com:WaykeYu/iptv_integ.git"  # 改用 SSH URL，避免需要 GitHub Token
LOCAL_REPO_PATH = "/home/runner/work/iptv_integ/iptv_integ"  # GitHub Actions 環境
FILE_PATH = os.path.join(LOCAL_REPO_PATH, "source/m3u/1888.m3u")

# **步驟 1：確認 GitHub 倉庫是否存在，否則 clone**
if not os.path.exists(LOCAL_REPO_PATH):
    print(f"⚠️ 當前環境中沒有 {LOCAL_REPO_PATH}，開始 Clone...")
    subprocess.run(["git", "clone", GITHUB_REPO_URL, LOCAL_REPO_PATH], check=True)
    print("✅ Clone 完成！")

# 目標網址
url = "https://www.yibababa.com/vod/"

# 設定 Selenium（無頭模式）
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

# 啟動 Selenium 瀏覽器
service = Service(ChromeDriverManager().install())
driver = None

try:
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    driver.implicitly_wait(10)  # 改進等待機制，確保 JavaScript 載入
    soup = BeautifulSoup(driver.page_source, "html.parser")
except Exception as e:
    print(f"❌ Selenium 啟動失敗: {e}")
    exit(1)
finally:
    if driver:
        driver.quit()

# **步驟 2：解析 HTML，找出所有 .m3u8 直播源**
pattern = re.compile(r"(.+?),\s*(http[^\s]+\.m3u8)")
channels = []

for tag in soup.find_all(["p", "div", "span", "a"]):  
    text = tag.get_text(separator="\n")
    matches = pattern.findall(text)
    for match in matches:
        channel_name = match[0].strip()
        stream_url = match[1].strip()
        channels.append((channel_name, stream_url))

# 轉換為 M3U 播放格式
m3u_content = "#EXTM3U\n"
for name, url in channels:
    m3u_content += f"#EXTINF:-1, {name}\n{url}\n"

# **步驟 3：拉取 GitHub 最新版本**
try:
    subprocess.run(["git", "pull", "origin", "main"], cwd=LOCAL_REPO_PATH, check=True)
except subprocess.CalledProcessError as e:
    print(f"⚠️ `git pull` 失敗: {e}")

# **步驟 4：寫入 `1888.m3u`**
with open(FILE_PATH, "w", encoding="utf-8") as f:
    f.write(m3u_content)

# **步驟 5：設定 Git 使用者資訊**
subprocess.run(["git", "config", "--local", "user.name", "WaykeYu"], cwd=LOCAL_REPO_PATH, check=True)
subprocess.run(["git", "config", "--local", "user.email", "waykeyu@example.com"], cwd=LOCAL_REPO_PATH, check=True)

# **步驟 6：確認是否有變更**
status_output = subprocess.run(["git", "status", "--porcelain"], cwd=LOCAL_REPO_PATH, capture_output=True, text=True)

if not status_output.stdout.strip():  # 沒有變更
    print("⚠️ `1888.m3u` 沒有變更，不需要提交！")
    exit(0)  # 直接結束程式

# **步驟 7：使用 `git` 提交並推送到 GitHub**
try:
    subprocess.run(["git", "add", FILE_PATH], cwd=LOCAL_REPO_PATH, check=True)
    subprocess.run(["git", "commit", "-m", "更新 1888.m3u，新增頻道列表"], cwd=LOCAL_REPO_PATH, check=True)
    subprocess.run(["git", "push", "origin", "main"], cwd=LOCAL_REPO_PATH, check=True)
    print("✅ `1888.m3u` 已成功推送到 GitHub！")
except subprocess.CalledProcessError as e:
    print("❌ Git 操作失敗！", e)
