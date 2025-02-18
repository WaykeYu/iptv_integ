import requests
import re

def download_m3u(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")
        return ""

def parse_m3u(content):
    channels = {}
    lines = content.splitlines()
    current_channel = None
    for line in lines:
        if line.startswith("#EXTINF"):  
            current_channel = line
        elif current_channel and line.startswith("http"):
            if line not in channels.values():  # 去除重覆頻道 URL
                channels[current_channel] = line
            current_channel = None
    return channels

def get_m3u_urls_from_github(repo_url):
    raw_base = "https://raw.githubusercontent.com/WaykeYu/iptv_integ/main/source/m3u/"
    api_url = "https://api.github.com/repos/WaykeYu/iptv_integ/contents/source/m3u"
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        files = response.json()
        return [raw_base + file["name"] for file in files if file["name"].endswith(".m3u")]
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch file list from GitHub: {e}")
        return []

def save_m3u(channels, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write("#EXTM3U\n")
        for info, url in channels.items():  # 保留分類, 去除重覆 URL
            file.write(f"{info}\n{url}\n")
    print(f"Merged file saved as {filename}")

# 獲取 GitHub M3U 文件的 URL
urls = get_m3u_urls_from_github("https://github.com/WaykeYu/iptv_integ/tree/main/source/m3u")

all_channels = {}
for url in urls:
    content = download_m3u(url)
    channels = parse_m3u(content)
    all_channels.update(channels)  # 合併並去重

save_m3u(all_channels, "merge.m3u")
