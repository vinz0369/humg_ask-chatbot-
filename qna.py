import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Đọc dữ liệu từ file faq.json
with open('/kaggle/working/faq_data.json', 'r', encoding='utf-8') as file:
    faq_data = json.load(file)

# Tạo danh sách câu hỏi và câu trả lời từ dữ liệu
questions = []
answers = []

# Lặp qua từng phần tử trong danh sách FAQ
for item in faq_data:
    questions.append(item['question'])
    answers.append(item['answer'])

# Tạo mô hình TF-IDF cho câu hỏi và câu trả lời
vectorizer_questions = TfidfVectorizer()
vectorizer_answers = TfidfVectorizer()

# Chuyển các câu hỏi và câu trả lời thành ma trận TF-IDF
tfidf_matrix_questions = vectorizer_questions.fit_transform(questions)
tfidf_matrix_answers = vectorizer_answers.fit_transform(answers)

# Hàm tìm kiếm câu hỏi tương tự
def search_similar_question(user_input, question_threshold=0.5, answer_threshold=0.3):
    # Bước 1: So sánh với câu hỏi
    user_tfidf_question = vectorizer_questions.transform([user_input])
    question_similarities = cosine_similarity(user_tfidf_question, tfidf_matrix_questions).flatten()
    best_question_index = question_similarities.argmax()
    
    if question_similarities[best_question_index] >= question_threshold:
        matched_question = questions[best_question_index]
        answer = answers[best_question_index]
        return matched_question, answer, question_similarities[best_question_index]
    
    # Bước 2: So sánh với câu trả lời nếu câu hỏi không đạt ngưỡng
    user_tfidf_answer = vectorizer_answers.transform([user_input])
    answer_similarities = cosine_similarity(user_tfidf_answer, tfidf_matrix_answers).flatten()
    best_answer_index = answer_similarities.argmax()
    
    if answer_similarities[best_answer_index] >= answer_threshold:
        matched_question = questions[best_answer_index]
        answer = answers[best_answer_index]
        return matched_question, answer, answer_similarities[best_answer_index]
    
    # Không tìm thấy câu trả lời phù hợp
    return None, "Xin lỗi, tôi không tìm thấy thông tin phù hợp.", 0.0

# Ví dụ sử dụng
user_question = "học công nghệ thông tin chất lượng cao làm gì"
matched_question, answer, similarity = search_similar_question(user_question)

if similarity > 0:
    print(f"Q: {matched_question}\nA: {answer} (Độ tương đồng: {similarity:.2f})")
else:
    print(f"A: {answer}")
