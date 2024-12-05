import requests
from bs4 import BeautifulSoup
import time
import json
import csv
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Tắt cảnh báo SSL
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# URL trang chính
MAIN_URL = "https://tuyensinh.humg.edu.vn/Pages/home.aspx"
BASE_URL = "https://tuyensinh.humg.edu.vn"

# Hàm tìm các URL ngành học
def get_program_urls(main_url):
    response = requests.get(main_url, verify=False)  # Bỏ qua SSL
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
    return program_urls

# Hàm lấy dữ liệu chi tiết từ từng ngành học
def crawl_program_details(url):
    try:
        # Bỏ qua SSL
        response = requests.get(url, verify=False)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "lxml")

        # Lấy tên ngành học
        title = soup.find("h1").get_text(strip=True) if soup.find("h1") else "Không rõ"

        # Lấy nội dung mô tả ngành
        description = ""
        description_div = soup.find("div", {"class": "content-detail"})
        if description_div:
            description = description_div.get_text(separator="\n", strip=True)

        return {
            
            "title": title,
            "description": description
        }
    except Exception as e:
        print(f"Lỗi khi crawl {url}: {e}")
        return {
            
            "title": "Không lấy được tiêu đề",
            "description": "Không lấy được nội dung"
        }


# Hàm lưu dữ liệu vào JSON
def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Hàm lưu dữ liệu vào CSV
def save_to_csv(data, filename):
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[ "title", "description"])
        writer.writeheader()
        writer.writerows(data)

# Main
if __name__ == "__main__":
    print("Bắt đầu crawl các URL ngành học...")
    program_urls = get_program_urls(MAIN_URL)
    print(f"Tìm thấy {len(program_urls)} ngành học!")

    # Crawl dữ liệu chi tiết từng ngành
    all_programs = []
    for idx, program_url in enumerate(program_urls):
        print(f"[{idx + 1}/{len(program_urls)}] Đang crawl: {program_url}")
        program_data = crawl_program_details(program_url)
        all_programs.append(program_data)
        time.sleep(1)  # Tránh quá tải server

    # Lưu kết quả vào JSON
    save_to_json(all_programs, "programs.json")
    print("Dữ liệu đã được lưu vào programs.json")

    # Lưu kết quả vào CSV
    save_to_csv(all_programs, "programs.csv")
    print("Dữ liệu đã được lưu vào programs.csv")
