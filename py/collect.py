import os
import requests
import schedule
import time
import sys
from datetime import datetime
from git import Repo, GitCommandError

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
