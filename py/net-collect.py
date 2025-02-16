import requests
from bs4 import BeautifulSoup
import os

# 目標網頁的 URL
url = 'https://www.yibababa.com/vod/'

# 發送 HTTP GET 請求
response = requests.get(url)

# 檢查請求是否成功
if response.status_code == 200:
    # 使用 BeautifulSoup 解析 HTML 內容
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 找到 <p> 標籤
    p_tag = soup.find('p', style='height: auto !important;')
    
    if p_tag:
        # 將 <p> 標籤中的內容轉換為字串
        p_content = p_tag.get_text(separator='\n')
        
        # 按行分割內容
        lines = p_content.split('\n')
        
        # 準備寫入的內容
        output_lines = []
        for line in lines:
            if line.strip() and ',' in line:
                channel_name, m3u8_url = line.strip().split(',', 1)
                output_lines.append(f"{channel_name},{m3u8_url}")
        
        # 將內容寫入 txt 文件
        output_content = "\n".join(output_lines)
        output_file_path = "adult1.txt"
        
        with open(output_file_path, "w", encoding="utf-8") as file:
            file.write(output_content)
        
        print(f"文件 {output_file_path} 已生成。")
        
        # 上傳到 GitHub
        github_repo = "https://github.com/WaykeYu/iptv_integ"
        github_path = "main/source/txt/adult1.txt"
        github_token = "your_github_token_here"  # 替換為你的 GitHub 個人訪問令牌
        
        # 讀取文件內容
        with open(output_file_path, "r", encoding="utf-8") as file:
            file_content = file.read()
        
        # 構建 GitHub API 請求
        github_api_url = f"https://api.github.com/repos/WaykeYu/iptv_integ/contents/source/txt/adult1.txt"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        data = {
            "message": "Add adult1.txt",
            "content": file_content.encode("utf-8").hex(),  # 將內容轉換為十六進制
            "branch": "main"
        }
        
        # 發送 PUT 請求上傳文件
        response = requests.put(github_api_url, json=data, headers=headers)
        
        if response.status_code == 201:
            print(f"文件已成功上傳到 GitHub: {github_repo}/tree/{github_path}")
        else:
            print(f"上傳到 GitHub 失敗，狀態碼: {response.status_code}")
            print(response.json())
    else:
        print("未找到指定的 <p> 標籤")
else:
    print(f"無法訪問網頁，狀態碼: {response.status_code}")
