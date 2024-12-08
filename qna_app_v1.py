import streamlit as st
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from underthesea import sent_tokenize  # Import hàm tách câu từ Underthesea

# Hàm tóm tắt văn bản (rút gọn câu trả lời dài)
def summarize_text(text, max_sentences=3):
    sentences = sent_tokenize(text)  # Chia đoạn văn thành các câu bằng Underthesea
    if len(sentences) > max_sentences:
        return " ".join(sentences[:max_sentences]) + "..."
    return text

# Load dữ liệu FAQ
with open('./faq_data (1).json', 'r', encoding='utf-8') as file:
    faq_data = json.load(file)

# Tạo danh sách câu hỏi và câu trả lời
questions = [item["question"] for item in faq_data]
answers = [item["answer"] for item in faq_data]

# Tạo mô hình TF-IDF cho câu hỏi
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(questions)

# Hàm tìm kiếm câu hỏi tương tự
def search_faq(user_input, threshold=0.5):
    user_tfidf = vectorizer.transform([user_input])
    similarities = cosine_similarity(user_tfidf, tfidf_matrix).flatten()
    best_index = similarities.argmax()

    if similarities[best_index] >= threshold:
        return questions[best_index], answers[best_index], similarities[best_index]
    return None, "Xin lỗi, không tìm thấy câu trả lời phù hợp.", 0.0

# Giao diện Streamlit
st.title("Hỏi đáp ngành học")
st.write("Nhập câu hỏi của bạn để tìm hiểu thêm về các ngành học!")

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
