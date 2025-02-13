import os
import requests
import schedule
import time
import sys
from datetime import datetime
from git import Repo

# 設定下載網址與儲存路徑
M3U_URL = "https://raw.githubusercontent.com/BigBigGrandG/IPTV-URL/release/Gather.m3u"
LOCAL_PATH = "./source/Gather.m3u"
GIT_REPO_PATH = "./iptv_integ"
GIT_REMOTE_URL = "git@github.com:WaykeYu/iptv_integ.git"

def ensure_git_repo():
    """確保本地 Git 倉庫存在，否則克隆"""
    if not os.path.exists(GIT_REPO_PATH):
        print("本地 Git 倉庫不存在，正在克隆...")
        Repo.clone_from(GIT_REMOTE_URL, GIT_REPO_PATH)
        print("克隆完成！")
    else:
        print("Git 倉庫已存在。")

def download_m3u():
    """下載 M3U 文件"""
    try:
        response = requests.get(M3U_URL)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(LOCAL_PATH), exist_ok=True)
        with open(LOCAL_PATH, "wb") as file:
            file.write(response.content)
        
        print(f"{datetime.now()}: 下載成功，存於 {LOCAL_PATH}")
        return True
    except Exception as e:
        print(f"下載失敗: {e}")
        return False

def push_to_github():
    """推送文件到 GitHub"""
    try:
        ensure_git_repo()
        repo = Repo(GIT_REPO_PATH)
        
        # 確保 Git 已經設定正確的 remote
        if "origin" not in [remote.name for remote in repo.remotes]:
            repo.create_remote("origin", GIT_REMOTE_URL)
        
        repo.git.add(LOCAL_PATH)
        repo.index.commit(f"Auto-update Gather.m3u at {datetime.now()}")
        origin = repo.remote(name="origin")
        origin.push()
        print("推送成功!")
    except Exception as e:
        print(f"推送失敗: {e}")

def job():
    """下載並推送"""
    if download_m3u():
        push_to_github()

# 允許手動觸發 `python script.py --once`
if __name__ == "__main__":
    if "--once" in sys.argv:
        job()
        sys.exit(0)

    # 設定每天上午 10:00 自動執行
    schedule.every().day.at("10:00").do(job)
    print("啟動 IPTV 下載任務。手動觸發請執行 `python script.py --once`")

    while True:
        schedule.run_pending()
        time.sleep(60)  # 每 60 秒檢查一次
