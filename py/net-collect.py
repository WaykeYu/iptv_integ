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

# 設定倉庫資訊
GITHUB_REPO_URL = "https://github.com/WaykeYu/iptv_integ.git"
LOCAL_REPO_PATH = "/home/runner/work/iptv_integ/iptv_integ"  # 你的 GitHub Actions 目錄
FILE_PATH = os.path.join(LOCAL_REPO_PATH, "source/txt/adult2.txt")

# 目標網址
url = "https://www.yibababa.com/vod/"

# 設定 Selenium（無頭模式）
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

# 啟動 Selenium 瀏覽器
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
driver.get(url)

# 等待 JavaScript 載入
time.sleep(5)

# 解析完整 HTML
soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

# 找出所有包含 .m3u8 連結的內容
pattern = re.compile(r"(.+?),\s*(http[^\s]+\.m3u8)")
channels = []

for tag in soup.find_all(["p", "div", "span", "a"]):  
    text = tag.get_text(separator="\n")
    matches = pattern.findall(text)
    for match in matches:
        channel_name = match[0].strip()
        stream_url = match[1].strip()
        channels.append((channel_name, stream_url))

# 轉換為 IPTV 播放格式
new_content = "#EXTM3U\n"
for name, url in channels:
    new_content += f"#EXTINF:-1, {name}\n{url}\n"

# **步驟 1：拉取 GitHub 最新版本**
subprocess.run(["git", "pull"], cwd=LOCAL_REPO_PATH, check=True)

# **步驟 2：讀取舊的 `adult2.txt`**
if os.path.exists(FILE_PATH):
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        existing_content = f.read()
else:
    existing_content = "#EXTM3U\n"

# **步驟 3：合併新舊內容（避免重複）**
all_lines = set(existing_content.strip().split("\n") + new_content.strip().split("\n"))
final_content = "\n".join(all_lines)

# **步驟 4：寫入 `adult2.txt`**
with open(FILE_PATH, "w", encoding="utf-8") as f:
    f.write(final_content)

# **步驟 5：使用 `git` 推送到 GitHub**
try:
    subprocess.run(["git", "add", FILE_PATH], cwd=LOCAL_REPO_PATH, check=True)
    subprocess.run(["git", "commit", "-m", "更新 adult2.txt，新增頻道列表"], cwd=LOCAL_REPO_PATH, check=True)
    subprocess.run(["git", "push", "origin", "main"], cwd=LOCAL_REPO_PATH, check=True)
    print("✅ `adult2.txt` 已成功推送到 GitHub！")
except subprocess.CalledProcessError as e:
    print("❌ Git 操作失敗！", e)
