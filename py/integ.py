import os
import re
import shutil
import requests
from pathlib import Path

# 1. Clone GitHub repo
repo_url = "https://github.com/WaykeYu/iptv_integ.git"
repo_dir = "iptv_integ"
m3u_dir = Path(repo_dir) / "source" / "m3u"

if not os.path.exists(repo_dir):
    os.system(f"git clone {repo_url}")

# 2. Find all .m3u files
m3u_files = list(m3u_dir.glob("*.m3u"))

# 3. Read and merge all .m3u files
channels = {}
grouped_channels = {}

for m3u_file in m3u_files:
    with open(m3u_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    current_group = "Uncategorized"
    for i in range(len(lines)):
        if lines[i].startswith("#EXTINF"):
            match = re.search(r'group-title="([^"]+)"', lines[i])
            if match:
                current_group = match.group(1)
            
            url = lines[i + 1].strip()
            if url not in channels:
                channels[url] = lines[i] + url + "\n"
                grouped_channels.setdefault(current_group, []).append(lines[i] + url + "\n")

# 4. Write merged file
output_file = m3u_dir / "merge.m3u"

with open(output_file, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for group, items in grouped_channels.items():
        f.write(f"\n# --- {group} ---\n")
        for item in items:
            f.write(item)

print(f"Merged file saved as {output_file}")
