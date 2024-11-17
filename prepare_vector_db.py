from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer

# Define paths
pdf_data_path = "data"
vector_db_path = "vectorstores/db_faiss"

def create_db_from_files():
    # Load PDF documents
    loader = DirectoryLoader(pdf_data_path, glob="*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)

    # Generate embeddings
    embedding_model = SentenceTransformer("distiluse-base-multilingual-cased-v2")
    embeddings = [embedding_model.encode(chunk.page_content) for chunk in chunks]

    # Create text-embedding pairs
    text_embeddings = list(zip([chunk.page_content for chunk in chunks], embeddings))

    # Create FAISS database (corrected argument passing)
    db = FAISS.from_embeddings(text_embeddings=text_embeddings)  # Pass 'text_embeddings' explicitly

    # Save database locally
    db.save_local(vector_db_path)
    return db

create_db_from_files()