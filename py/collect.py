import os
import requests
import subprocess

# GitHub 倉庫資訊
GITHUB_REPO = "WaykeYu/iptv_integ"
BRANCH = "main"

# 下載文件的 URL
FILE_URLS = [
    "https://aktv.top/live.m3u",
    "https://raw.githubusercontent.com/WaykeYu/MyTV_tw/refs/heads/main/TW_allsource",
    "https://epg.pw/test_channels_taiwan.m3u",
    "https://iptv-org.github.io/iptv/countries/tw.m3u",
    "https://raw.githubusercontent.com/TVzhiboyuandaka/zhiboyuandaka.github.io/main/20220910ZQ.m3u",
    "https://raw.githubusercontent.com/hujingguang/ChinaIPTV/main/cnTV_AutoUpdate.m3u8",
    "https://raw.githubusercontent.com/WaykeYu/iptv_integ/refs/heads/main/source/txt/4gTV",
    "https://raw.githubusercontent.com/WaykeYu/iptv_integ/refs/heads/main/source/txt/UBTV0318",
    "https://raw.githubusercontent.com/WaykeYu/iptv_integ/refs/heads/main/source/txt/adult1",
    "https://raw.githubusercontent.com/YanG-1989/m3u/refs/heads/main/Gather.m3u"
]

# 存儲目錄
M3U_DIR = "source/m3u/"
TXT_DIR = "source/txt/"

# 下載檔案
def download_file(url):
    filename = os.path.basename(url)
    file_ext = os.path.splitext(filename)[1].lower()

    # 判斷存放位置
    if file_ext == ".m3u":
        save_path = os.path.join(M3U_DIR, filename)
    elif file_ext == ".txt" or file_ext == "":
        save_path = os.path.join(TXT_DIR, filename + ".txt")  # 確保存為 .txt
    else:
        print(f"未知文件類型: {filename}，跳過下載")
        return None

    # 下載文件
    response = requests.get(url)
    if response.status_code == 200:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)  # 確保目錄存在
        with open(save_path, "wb") as f:
            f.write(response.content)
        print(f"下載完成: {save_path}")
        return save_path
    else:
        print(f"下載失敗: {url}")
        return None

# 轉換 TXT 為 M3U 格式
def convert_txt_to_m3u(txt_path):
    m3u_path = txt_path.replace(TXT_DIR, M3U_DIR).replace(".txt", ".m3u")
    try:
        with open(txt_path, "r", encoding="utf-8") as txt, open(m3u_path, "w", encoding="utf-8") as m3u:
            m3u.write("#EXTM3U\n")
            for line in txt:
                if line.strip():
                    m3u.write(f"#EXTINF:-1,{line.strip()}\n{line.strip()}\n")
        print(f"轉換完成: {m3u_path}")
        return m3u_path
    except Exception as e:
        print(f"轉換失敗: {e}")
        return None

# Git 操作
def git_push(files):
    try:
        subprocess.run(["git", "pull"], check=True)
        subprocess.run(["git", "add"] + files, check=True)
        subprocess.run(["git", "commit", "-m", "Auto update IPTV files"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("文件已推送到 GitHub！")
    except subprocess.CalledProcessError as e:
        print(f"Git 操作失敗: {e}")

if __name__ == "__main__":
    updated_files = []

    for url in FILE_URLS:
        file_path = download_file(url)
        if file_path:
            updated_files.append(file_path)
            # 如果是 .txt，則轉換為 .m3u
            if file_path.endswith(".txt"):
                converted_path = convert_txt_to_m3u(file_path)
                if converted_path:
                    updated_files.append(converted_path)

    if updated_files:
        git_push(updated_files)
