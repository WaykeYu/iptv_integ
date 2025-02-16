import requests
from bs4 import BeautifulSoup

# 目標網頁的 URL
url = 'https://www.yibababa.com/vod/'

# 自定義請求頭
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 發送 HTTP GET 請求
response = requests.get(url, headers=headers)

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
    else:
        print("未找到指定的 <p> 標籤")
else:
    print(f"無法訪問網頁，狀態碼: {response.status_code}")
