import streamlit as st
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from underthesea import sent_tokenize

def summarize_with_tfidf(text, max_sentences=3):
    """
    Tóm tắt văn bản bằng cách chọn các câu quan trọng nhất.
    - text: Văn bản đầu vào.
    - max_sentences: Số lượng câu tối đa trong bản tóm tắt.
    """
    # Tách văn bản thành danh sách câu
    sentences = sent_tokenize(text)
    if len(sentences) <= max_sentences:
        return text  # Nếu số câu ít hơn max_sentences, trả về văn bản gốc
    
    # Tính TF-IDF cho các câu
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(sentences)
    
    # Tính độ quan trọng của mỗi câu bằng cách đo tương tự ngữ nghĩa
    sentence_scores = cosine_similarity(tfidf_matrix, np.asarray(tfidf_matrix.sum(axis=0)).reshape(1, -1))
    
    # Đánh số thứ tự để bảo toàn vị trí
    scored_sentences = list(enumerate(sentence_scores.flatten()))
    
    # Sắp xếp câu theo điểm quan trọng
    sorted_sentences = sorted(scored_sentences, key=lambda x: x[1], reverse=True)
    
    # Chọn các câu quan trọng nhất
    top_sentences = sorted(sorted_sentences[:max_sentences], key=lambda x: x[0])  # Giữ thứ tự câu gốc
    summary = " ".join([sentences[idx] for idx, _ in top_sentences])
    return summary

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
    """
    Tìm kiếm câu hỏi tương tự trong FAQ.
    - user_input: Câu hỏi của người dùng.
    - threshold: Ngưỡng độ tương đồng tối thiểu để trả lời.
    """
    user_tfidf = vectorizer.transform([user_input])
    similarities = cosine_similarity(user_tfidf, np.asarray(tfidf_matrix)).flatten()
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
        summarized_answer = summarize_with_tfidf(answer, max_sentences=3)
        
        st.write(f"**Câu hỏi gần nhất:** {matched_question}")
        st.write(f"**Câu trả lời tóm tắt:** {summarized_answer}")
        st.write(f"**Độ tương đồng:** {similarity:.2f}")
        with st.expander("Xem đầy đủ câu trả lời"):
            st.write(answer)
    else:
        st.write(answer)
