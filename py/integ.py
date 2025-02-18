import os
import re
import subprocess
from pathlib import Path

# GitHub Repo 設定
repo_url = "https://github.com/WaykeYu/iptv_integ.git"
repo_dir = "iptv_integ"
output_file = Path(repo_dir) / "merge.m3u"

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 命令執行失敗: {command}")
        print(result.stderr)
        exit(1)
    return result.stdout

try:
    # 1. 克隆 GitHub 儲存庫（如果尚未存在）
    if not os.path.exists(repo_dir) or not os.path.exists(os.path.join(repo_dir, ".git")):
        run_command(f"git clone {repo_url}")

    # 2. 讀取所有 .m3u 文件（來自 source/m3u/）
    m3u_dir = Path(repo_dir) / "source" / "m3u"
    m3u_files = list(m3u_dir.glob("*.m3u"))

    if not m3u_dir.exists() or not m3u_files:
        print(f"❌ 沒有找到任何 .m3u 文件在 {m3u_dir}")
        exit(1)

    grouped_channels = {}
    group_title_pattern = re.compile(r'group-title="([^"]+)"')

    for m3u_file in m3u_files:
        with open(m3u_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        current_group = "Uncategorized"
        for i in range(len(lines)):
            if lines[i].startswith("#EXTINF"):
                match = group_title_pattern.search(lines[i])
                if match:
                    current_group = match.group(1)
                
                url = lines[i + 1].strip()
                grouped_channels.setdefault(current_group, []).append(lines[i] + url + "\n")

    # 3. 確保 `merge.m3u` 存在於 repo 根目錄
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for group, items in grouped_channels.items():
            f.write(f"\n# --- {group} ---\n")
            f.writelines(items)

    print(f"📂 merge.m3u 已成功建立於 {output_file}")

    # 4. 提交並推送到 GitHub
    os.chdir(repo_dir)  # 進入 repo 目錄
    run_command("git pull origin main")  # 確保是最新版本
    run_command("git add merge.m3u")
    run_command('git commit -m "更新合併後的 M3U 頻道列表"')
    run_command("git push origin main")  # 推送變更

    print("🚀 merge.m3u 已成功推送至 GitHub！")

except Exception as e:
    print(f"❌ 發生錯誤: {e}")
    exit(1)
