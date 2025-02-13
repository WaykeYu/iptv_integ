import os
import requests
import schedule
import time
import sys
from datetime import datetime
from git import Repo, GitCommandError
import subprocess

# 嘗試引入 schedule，如果沒有則自動安裝
try:
    import schedule
except ModuleNotFoundError:
    print("未找到 `schedule`，正在安裝...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "schedule"])
    import schedule  # 安裝後再引入

# 設定下載網址與儲存路徑
M3U_URL = "https://raw.githubusercontent.com/BigBigGrandG/IPTV-URL/release/Gather.m3u"
LOCAL_PATH = "./source/Gather.m3u"
GIT_REPO_PATH = "./iptv_integ"
GIT_REMOTE_URL = "git@github.com:WaykeYu/iptv_integ.git"

# 記錄下載的 ETag，減少重複下載
ETAG_FILE = "./source/.etag"


def ensure_git_repo():
    """確保本地 Git 倉庫存在，否則克隆"""
    if not os.path.exists(GIT_REPO_PATH):
        print("本地 Git 倉庫不存在，正在克隆...")
        Repo.clone_from(GIT_REMOTE_URL, GIT_REPO_PATH)
        print("克隆完成！")
    else:
        print("Git 倉庫已存在。")


def get_etag():
    """讀取本地保存的 ETag"""
    if os.path.exists(ETAG_FILE):
        with open(ETAG_FILE, "r") as f:
            return f.read().strip()
    return None


def save_etag(etag):
    """儲存新的 ETag"""
    with open(ETAG_FILE, "w") as f:
        f.write(etag)


def download_m3u():
    """下載 M3U 文件，使用 ETag 檢查是否有更新"""
    headers = {}
    etag = get_etag()
    if etag:
        headers["If-None-Match"] = etag  # 使用 ETag 減少不必要的下載

    try:
        response = requests.get(M3U_URL, headers=headers, timeout=10)  # 設定超時 10 秒
        if response.status_code == 304:
            print(f"{datetime.now()}: M3U 無更新，跳過下載")
            return False  # 沒有新內容

        response.raise_for_status()  # 檢查是否有 HTTP 錯誤
        os.makedirs(os.path.dirname(LOCAL_PATH), exist_ok=True)

        with open(LOCAL_PATH, "wb") as file:
            file.write(response.content)

        # 儲存新的 ETag
        if "ETag" in response.headers:
            save_etag(response.headers["ETag"])

        print(f"{datetime.now()}: 下載成功，存於 {LOCAL_PATH}")
        return True
    except requests.exceptions.Timeout:
        print("❌ 下載超時，請稍後再試")
    except requests.exceptions.HTTPError as errh:
        print(f"❌ HTTP 錯誤: {errh}")
    except requests.exceptions.RequestException as err:
        print(f"❌ 下載失敗: {err}")

    return False  # 如果發生錯誤，返回 False


def push_to_github():
    """推送文件到 GitHub"""
    try:
        ensure_git_repo()
        repo = Repo(GIT_REPO_PATH)

        # 確保 Git 倉庫是最新的
        repo.remotes.origin.fetch()
        repo.git.checkout("main")
        repo.git.pull("origin", "main")

        # 檢查是否有變更，避免無意義提交
        repo.git.add(LOCAL_PATH)
        if repo.is_dirty():  # 只有文件變更時才提交
            repo.index.commit(f"Auto-update Gather.m3u at {datetime.now()}")
            repo.remotes.origin.push()
            print("✅ 推送成功！")
        else:
            print("⚡ 未檢測到變更，跳過推送")
    except GitCommandError as e:
        print(f"❌ Git 操作失敗: {e}")
    except Exception as e:
        print(f"❌ 推送失敗: {e}")


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
    print("⏳ 啟動 IPTV 下載任務。手動觸發請執行 `python script.py --once`")

    while True:
        schedule.run_pending()
        time.sleep(60)  # 每 60 秒檢查一次
