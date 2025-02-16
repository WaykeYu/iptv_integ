import requests
from bs4 import BeautifulSoup

# 目標 URL
url = "https://www.yibababa.com/vod/"

# 設定 User-Agent
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 發送 HTTP GET 請求
response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 查找特定 <p> 標籤
    target_p = soup.find("p", class_="w3-large w3-text-indigo", id="18", style="color: blue;")
    
    if target_p:
        channel_name = target_p.text.strip()
        
        # 假設有對應的 m3u8 直播源（這部分需要從網頁進一步抓取）
        stream_url = "https://example.com/stream.m3u8"  # 這裡應該用實際的直播源

        # 轉換為 txt 格式
        txt_content = f"#EXTM3U\n#EXTINF:-1, {channel_name}\n{stream_url}\n"
        
        # 將內容寫入 adult1.txt
        file_path = "adult1.txt"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(txt_content)

        print(f"{file_path} 已成功生成！")

        # ======== 下面是 GitHub 上傳部分 ========
        github_repo = "WaykeYu/iptv_integ"
        github_branch = "main"
        github_token = "your_personal_access_token"  # 這裡需要你的 GitHub Token
        github_file_path = "source/txt/adult1.txt"
        github_api_url = f"https://api.github.com/repos/{github_repo}/contents/{github_file_path}"

        # 讀取檔案內容並轉為 base64
        import base64
        with open(file_path, "rb") as file:
            encoded_content = base64.b64encode(file.read()).decode("utf-8")

        # 取得 GitHub 上該檔案的 SHA 值（如果檔案已存在，需提供 SHA 以更新）
        response = requests.get(github_api_url, headers={"Authorization": f"token {github_token}"})
        sha = response.json().get("sha", "")

        # 設置 GitHub API 上傳請求
        data = {
            "message": "更新成人直播源",
            "content": encoded_content,
            "branch": github_branch
        }
        if sha:
            data["sha"] = sha  # 如果檔案已存在，則添加 SHA 值

        # 發送 PUT 請求上傳至 GitHub
        upload_response = requests.put(github_api_url, json=data, headers={"Authorization": f"token {github_token}"})

        if upload_response.status_code in [200, 201]:
            print("adult1.txt 已成功上傳至 GitHub！")
        else:
            print("上傳失敗！", upload_response.json())

    else:
        print("找不到符合條件的 <p> 標籤")
else:
    print(f"請求失敗，狀態碼：{response.status_code}")
