import requests
import re
import os
import subprocess

# GitHub 設定
LOCAL_REPO_PATH = "/home/runner/work/iptv_integ/iptv_integ"
FILE_PATH = os.path.join(LOCAL_REPO_PATH, "source/m3u/1888.m3u")

# 目標資料來源（JS/JSON/API，不需要 Selenium）
SOURCES = {
    "yibababa_vod": "https://www.yibababa.com/static/js/playerconfig.js",
    "aktv": "https://aktv.top/live.json",
    "yibababa_tw": "https://yibababa.com/live/tw.json"
}

# 分類關鍵字
CATEGORIES = {
    "成人頻道": ["成人", "18", "X", "精", "香蕉"],
    "體育頻道": ["體育", "足球", "NBA", "ESPN"],
    "新聞頻道": ["新聞", "CCTV", "BBC", "東森", "中天", "民視"],
    "綜藝頻道": ["娛樂", "綜藝", "八大"],
    "電影頻道": ["電影", "HBO", "Cinemax"],
    "台湾直播源": ["台", "民視", "中視", "華視", "三立"]
}

# 抓取內容
def fetch(url):
    print(f"📡 抓取來源: {url}")
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.text
    except:
        print(f"❌ 抓取失敗: {url}")
        return ""

# 從 JS / JSON 中找 m3u8
def extract_m3u8(text):
    # 名稱,URL
    pattern = re.compile(r'"?name"?:\s*"?(.*?)"?[, ]+"?url"?:\s*"?(http.*?\.m3u8)"?', re.IGNORECASE)
    results = pattern.findall(text)

    if results:
        return [(name.strip(), url.strip()) for name, url in results]

    # 備援：通用 m3u8 URL
    pattern2 = re.compile(r"(.*?)\s*(http.*?\.m3u8)")
    return [(m[0].strip(), m[1].strip()) for m in pattern2.findall(text)]

# 分類
def classify(name):
    for cat, keywords in CATEGORIES.items():
        if any(k in name for k in keywords):
            return cat
    return "未分類頻道"

# 建立 M3U
def build_m3u(channels):
    m3u = "#EXTM3U\n"

    grouped = {}
    for name, url in channels:
        cat = classify(name)
        grouped.setdefault(cat, []).append((name, url))

    for cat, items in grouped.items():
        m3u += f"\n#EXTGRP:{cat}\n"
        for name, url in items:
            m3u += f"#EXTINF:-1,{name}\n{url}\n"

    return m3u

# 寫入 GitHub 檔案
def write_to_repo(text):
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write(text)

    subprocess.run(["git", "config", "--local", "user.name", "WaykeYu"], cwd=LOCAL_REPO_PATH)
    subprocess.run(["git", "config", "--local", "user.email", "waykeyu@example.com"], cwd=LOCAL_REPO_PATH)

    subprocess.run(["git", "add", FILE_PATH], cwd=LOCAL_REPO_PATH)
    status = subprocess.run(["git", "status", "--porcelain"], cwd=LOCAL_REPO_PATH, capture_output=True, text=True)

    if not status.stdout.strip():
        print("⚠️ 沒有變更，不推送。")
        return

    subprocess.run(["git", "commit", "-m", "自動更新 IPTV 資料（無 Selenium 版本）"], cwd=LOCAL_REPO_PATH)
    subprocess.run(["git", "push", "origin", "main"], cwd=LOCAL_REPO_PATH)
    print("✅ 已推送更新到 GitHub！")

def main():
    all_channels = []

    # 逐一抓取
    for name, url in SOURCES.items():
        text = fetch(url)
        if text:
            channels = extract_m3u8(text)
            all_channels.extend(channels)

    # 去掉重複
    unique = list(dict((url, name) for name, url in all_channels).items())
    unique = [(name, url) for url, name in unique]

    # 生成 M3U
    m3u_text = build_m3u(unique)

    # 寫入 GitHub
    write_to_repo(m3u_text)

if __name__ == "__main__":
    main()
