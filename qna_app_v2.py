import re
import json
from underthesea import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

# 1. Tiền xử lý văn bản

def preprocess_text(text):
    """
    Tiền xử lý văn bản: Loại bỏ ký tự đặc biệt, tách từ.
    """
    # Chuyển thành chữ thường
    text = text.lower()
    # Loại bỏ ký tự đặc biệt và số
    text = re.sub(r'[^\w\s]', '', text)  # Loại bỏ dấu câu
    text = re.sub(r'\d+', '', text)      # Loại bỏ số
    # Tách từ
    tokens = word_tokenize(text)
    # Ghép lại thành câu
    return " ".join(tokens)

# 2. Load dữ liệu FAQ và tiền xử lý câu hỏi
with open('./faq_data (2).json', 'r', encoding='utf-8') as file:
    faq_data = json.load(file)

questions = [item["question"] for item in faq_data]
answers = [item["answer"] for item in faq_data]

# Tiền xử lý các câu hỏi trong FAQ
preprocessed_questions = [preprocess_text(q) for q in questions]

# 3. Tạo TF-IDF vectorizer từ câu hỏi đã tiền xử lý
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(preprocessed_questions)

# 4. Hàm tóm tắt văn bản
def summarize_text(text, max_sentences=3):
    """
    Tóm tắt câu trả lời: chỉ lấy một số câu đầu tiên nếu câu trả lời quá dài.
    """
    sentences = sent_tokenize(text)  # Chia đoạn văn thành các câu bằng Underthesea
    if len(sentences) > max_sentences:
        return " ".join(sentences[:max_sentences]) + "..."
    return text

# 5. Hàm tìm kiếm câu hỏi tương tự
def search_faq(user_input, threshold=0.5):
    """
    Tìm câu hỏi trong FAQ tương tự nhất với đầu vào của người dùng.
    """
    # Tiền xử lý câu hỏi đầu vào
    preprocessed_input = preprocess_text(user_input)
    # Biến đổi thành vector TF-IDF
    user_tfidf = vectorizer.transform([preprocessed_input])
    similarities = cosine_similarity(user_tfidf, tfidf_matrix).flatten()
    best_index = similarities.argmax()

    if similarities[best_index] >= threshold:
        return questions[best_index], answers[best_index], similarities[best_index]
    return None, "Xin lỗi, không tìm thấy câu trả lời phù hợp.", 0.0

# 6. Giao diện Streamlit
st.title("Hỏi đáp ngành học - HUMG")
st.markdown("""
### Nhập câu hỏi của bạn để tìm hiểu thêm về các ngành học
Hệ thống cung cấp các thông tin về:
- ✅ **Thông tin tổng quan**
- 💼 **Cơ hội việc làm**
- 📚 **Điều kiện học tập và chính sách hỗ trợ sinh viên**
- 🕒 **Thời gian đào tạo và mức học phí**
- 🎓 **Cơ hội học bổng và mức lương sau khi ra trường**
- 📞 **Thông tin liên hệ của các ngành học**
""", unsafe_allow_html=True)

# Nhận câu hỏi từ người dùng
user_question = st.text_input("Nhập câu hỏi của bạn:")

if user_question:
    matched_question, answer, similarity = search_faq(user_question)
    if similarity > 0:
        # Tóm tắt câu trả lời nếu quá dài
        summarized_answer = summarize_text(answer, max_sentences=3)
        
        st.write(f"**Câu hỏi gần nhất:** {matched_question}")
        st.write(f"**Câu trả lời tóm tắt:** {summarized_answer}")
        st.write(f"**Độ tương đồng:** {similarity:.2f}")
        with st.expander("Xem đầy đủ câu trả lời"):
            st.write(answer)
    else:
        st.write(answer)
import pandas as pd

