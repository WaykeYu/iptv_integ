import os
import requests
import subprocess

# 設置 GitHub 倉庫相關信息
GITHUB_REPO = "WaykeYu/iptv_integ"
BRANCH = "main"

# M3U 文件存放路徑
M3U_URL = "https://aktv.top/live.m3u"
M3U_PATH = "source/m3u/live.m3u"

# 下載 M3U 文件
def download_m3u():
    response = requests.get(M3U_URL)
    if response.status_code == 200:
        os.makedirs(os.path.dirname(M3U_PATH), exist_ok=True)  # 確保目錄存在
        with open(M3U_PATH, "wb") as f:
            f.write(response.content)
        print(f"下載完成: {M3U_PATH}")
    else:
        print("下載失敗！")

# Git 操作
def git_push():
    try:
        subprocess.run(["git", "pull"], check=True)
        subprocess.run(["git", "add", M3U_PATH], check=True)
        subprocess.run(["git", "commit", "-m", "Auto update live.m3u"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("文件已推送到 GitHub！")
    except subprocess.CalledProcessError as e:
        print(f"Git 操作失敗: {e}")

if __name__ == "__main__":
    download_m3u()
    git_push()
