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
    current_url = None
    for line in lines:
        if line.startswith("#EXTINF"):  
            current_channel = line
        elif current_channel and line.startswith("http"):
            current_url = line
            if current_url not in channels.values():
                channels[current_channel] = current_url
            current_channel = None
            current_url = None
    return channels

def save_m3u(channels, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write("#EXTM3U\n")
        for info, url in sorted(channels.items()):
            file.write(f"{info}\n{url}\n")
    print(f"Merged file saved as {filename}")

# M3U 文件的 URL
urls = [
    "https://raw.githubusercontent.com/WaykeYu/iptv_integ/refs/heads/main/source/m3u/1888.m3u",
    "https://raw.githubusercontent.com/WaykeYu/iptv_integ/refs/heads/main/source/m3u/20220910ZQ.m3u",
    "https://raw.githubusercontent.com/WaykeYu/iptv_integ/refs/heads/main/merge.m3u"
]

all_channels = {}
for url in urls:
    content = download_m3u(url)
    channels = parse_m3u(content)
    all_channels.update(channels)

save_m3u(all_channels, "merge.m3u")
