import requests

def download_m3u(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")
        return ""

def parse_m3u(content):
    channels = []
    lines = content.splitlines()
    current_channel = None
    for line in lines:
        if line.startswith("#EXTINF"):  
            current_channel = line
        elif current_channel and line.startswith("http"):
            channels.append((current_channel, line))
            current_channel = None
    return channels

def save_m3u(channels, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write("#EXTM3U\n")
        for info, url in channels:
            file.write(f"{info}\n{url}\n")
    print(f"Merged file saved as {filename}")

# M3U 文件的 URL
urls = [
    "https://raw.githubusercontent.com/WaykeYu/iptv_integ/refs/heads/main/source/m3u/1888.m3u",
    "https://raw.githubusercontent.com/WaykeYu/iptv_integ/refs/heads/main/source/m3u/20220910ZQ.m3u",
    "https://raw.githubusercontent.com/WaykeYu/iptv_integ/refs/heads/main/merge.m3u"
]

all_channels = []
for url in urls:
    content = download_m3u(url)
    channels = parse_m3u(content)
    all_channels.extend(channels)

save_m3u(all_channels, "merge.m3u")
