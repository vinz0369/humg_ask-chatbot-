import csv
import re
import json

# Đọc file CSV
csv_file = '/kaggle/working/programs.csv'  # Đường dẫn tới file CSV
faq_data = []

# Mở và đọc CSV
with open(csv_file, mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)
    
    # Bỏ qua tiêu đề (nếu có)
    next(reader)
    
    # Lặp qua từng dòng trong file CSV
    for row in reader:
        # Giả sử rằng cột đầu tiên là tiêu đề và cột thứ hai là mô tả
        title = row[0]
        description = row[1]
        
        # Sử dụng regex để tách các mục có dạng 1., 2., 3., ...
        pattern = r"(\d+\.\s.+?)\n(.*?)(?=\n\d+\.\s|\Z)"
        matches = re.findall(pattern, description, re.DOTALL)
        
        # Lặp qua các kết quả khớp và lưu vào danh sách
        for match in matches:
            question = match[0].strip()  # Lấy câu hỏi (phần đánh số)
            answer = match[1].strip()  # Lấy câu trả lời (phần dưới câu hỏi)
            
            # Thêm phần title vào câu hỏi
            question_with_title = f"{title}: {question}"  # Ghép title vào câu hỏi
            
            # Lưu câu hỏi và câu trả lời vào danh sách faq_data
            faq_data.append({"question": question_with_title, "answer": answer})

# Lưu kết quả vào file JSON
with open('faq_data.json', 'w', encoding='utf-8') as json_file:
    json.dump(faq_data, json_file, ensure_ascii=False, indent=4)

# In kết quả (tuỳ chọn)
print(json.dumps(faq_data, ensure_ascii=False, indent=4))
