from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# 設置 ChromeDriver 路徑
chrome_driver_path = "/path/to/chromedriver"  # 替換為你的 ChromeDriver 路徑
service = Service(chrome_driver_path)
options = webdriver.ChromeOptions()

# 啟動瀏覽器
driver = webdriver.Chrome(service=service, options=options)

# 訪問目標網頁
url = 'https://www.yibababa.com/vod/'
driver.get(url)

# 等待頁面加載完成
time.sleep(5)  # 根據實際情況調整等待時間

# 獲取頁面內容
page_source = driver.page_source

# 使用 BeautifulSoup 解析內容
from bs4 import BeautifulSoup
soup = BeautifulSoup(page_source, 'html.parser')

# 查找目標 <p> 標籤
p_tag = soup.find('p', style='height: auto !important;')  # 根據實際情況修改

if p_tag:
    # 提取內容
    p_content = p_tag.get_text(separator='\n')
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

# 關閉瀏覽器
driver.quit()
