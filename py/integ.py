import os
import re
from pathlib import Path

# GitHub Repo 資訊
repo_url = "https://github.com/WaykeYu/iptv_integ.git"
repo_dir = "iptv_integ"
m3u_dir = Path(repo_dir) / "source" / "m3u"
output_file = m3u_dir / "merge.m3u"

# 1. 克隆 GitHub 儲存庫（如果尚未存在）
if not os.path.exists(repo_dir):
    os.system(f"git clone {repo_url}")

# 2. 讀取所有 .m3u 文件
m3u_files = list(m3u_dir.glob("*.m3u"))
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

# 3. 寫入合併檔案 merge.m3u
with open(output_file, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for group, items in grouped_channels.items():
        f.write(f"\n# --- {group} ---\n")
        for item in items:
            f.write(item)

print(f"Merged file saved at {output_file}")

# 4. 提交並推送到 GitHub
os.chdir(repo_dir)  # 進入 repo 目錄
os.system("git pull origin main")  # 確保是最新版本
os.system("git add source/m3u/merge.m3u")
os.system('git commit -m "Auto-merged M3U files"')
os.system("git push origin main")  # 推送變更

print("merge.m3u 已成功推送至 GitHub！")
