import requests
from bs4 import BeautifulSoup
import re
import base64
import json

# 目標 URL
url = "https://www.yibababa.com/vod/"

# 設定 User-Agent 避免被封鎖
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 發送 HTTP GET 請求
response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    # 找到 <p> 標籤，style 為 "height: auto !important;"
    target_p = soup.find("p", style="height: auto !important;")
    
    if target_p:
        text_content = target_p.get_text("\n")  # 取得文字內容並換行分隔
        lines = text_content.split("\n")  # 以換行拆分

        # 解析頻道名稱與 m3u8 連結
        channels = []
        pattern = re.compile(r"(.+?),\s*(http[^\s]+\.m3u8)")  # 匹配「頻道名稱, 直播源」格式

        for line in lines:
            match = pattern.search(line)
            if match:
                channel_name = match.group(1).strip()
                stream_url = match.group(2).strip()
                channels.append((channel_name, stream_url))

        # 轉換為 IPTV 播放格式
        new_content = ""
        for name, url in channels:
            new_content += f"#EXTINF:-1, {name}\n{url}\n"

        # ======== GitHub 讀取 & 更新部分 ========
        github_repo = "WaykeYu/iptv_integ"
        github_branch = "main"
        github_token = "your_personal_access_token"  # 需替換為你的 GitHub Token
        github_file_path = "source/txt/adult2.txt"
        github_api_url = f"https://api.github.com/repos/{github_repo}/contents/{github_file_path}"

        # 取得 GitHub 上的現有檔案內容
        response = requests.get(github_api_url, headers={"Authorization": f"token {github_token}"})
        if response.status_code == 200:
            existing_data = response.json()
            sha = existing_data.get("sha", "")
            existing_content = base64.b64decode(existing_data["content"]).decode("utf-8")

            # 合併新舊內容
            final_content = existing_content.strip() + "\n" + new_content.strip()

        else:
            # 若檔案不存在，則直接使用新的內容
            sha = None
            final_content = "#EXTM3U\n" + new_content

        # 轉換為 Base64
        encoded_content = base64.b64encode(final_content.encode("utf-8")).decode("utf-8")

        # 準備 GitHub API 上傳請求
        data = {
            "message": "更新 adult2.txt，新增頻道列表",
            "content": encoded_content,
            "branch": github_branch
        }
        if sha:
            data["sha"] = sha  # 若檔案已存在，則提供 SHA 值

        # 發送 PUT 請求上傳至 GitHub
        upload_response = requests.put(github_api_url, json=data, headers={"Authorization": f"token {github_token}"})

        if upload_response.status_code in [200, 201]:
            print("adult2.txt 已成功更新至 GitHub！")
        else:
            print("上傳失敗！", upload_response.json())

    else:
        print("找不到符合條件的 <p> 標籤")

else:
    print(f"請求失敗，狀態碼：{response.status_code}")

