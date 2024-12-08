import requests
from bs4 import BeautifulSoup
import time
import json
import csv
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Tắt cảnh báo SSL
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# URL trang chính và trang cơ sở
MAIN_URL = "https://tuyensinh.humg.edu.vn/Pages/home.aspx"
BASE_URL = "https://tuyensinh.humg.edu.vn"

# Bước 1: Tìm tất cả URL ngành học từ trang chính
print("Bắt đầu crawl các URL ngành học...")
response = requests.get(MAIN_URL, verify=False)  # Bỏ qua SSL
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, "lxml")

# Tìm tất cả các liên kết có chứa "ItemID"
links = soup.find_all("a", href=True)
program_urls = []
for link in links:
    href = link["href"]
    if "chuong-trinh-dao-tao-HUMG.aspx?ItemID=" in href:
        full_url = BASE_URL + href if href.startswith("/") else href
        program_urls.append(full_url)

print(f"Tìm thấy {len(program_urls)} ngành học!")

# Bước 2: Crawl chi tiết dữ liệu từng ngành
all_programs = []
for idx, program_url in enumerate(program_urls):
    print(f"[{idx + 1}/{len(program_urls)}] Đang crawl: {program_url}")
    try:
        response = requests.get(program_url, verify=False)  # Bỏ qua SSL
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "lxml")

        # Lấy tiêu đề ngành học (thẻ h1)
        title = soup.find("h1").get_text(strip=True) if soup.find("h1") else "Không rõ"

        # Lấy nội dung mô tả ngành (từ các thẻ <p>)
        description = ""
        description_div = soup.find("div", {"class": "contentContainer"})
        if description_div:
            paragraphs = description_div.find_all("p")
            description = "\n".join(p.get_text(strip=True) for p in paragraphs)

        # Thêm dữ liệu vào danh sách
        all_programs.append({
            "title": title,
            "description": description
        })
    except Exception as e:
        print(f"Lỗi khi crawl {program_url}: {e}")
        all_programs.append({
            "title": "Không lấy được tiêu đề",
            "description": "Không lấy được nội dung"
        })

    time.sleep(1)  # Tránh quá tải server

# Bước 3: Lưu dữ liệu vào file JSON
with open("programs.json", "w", encoding="utf-8") as json_file:
    json.dump(all_programs, json_file, ensure_ascii=False, indent=4)

print("Dữ liệu đã được lưu vào programs.json")

# Bước 4: Lưu dữ liệu vào file CSV
with open("programs.csv", "w", encoding="utf-8-sig", newline="") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=["title", "description"])
    writer.writeheader()
    writer.writerows(all_programs)

print("Dữ liệu đã được lưu vào programs.csv")
