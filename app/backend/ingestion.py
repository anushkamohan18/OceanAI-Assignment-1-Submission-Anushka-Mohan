import os
from typing import List
import chromadb
from chromadb.utils import embedding_functions
import fitz  # PyMuPDF
import json
from bs4 import BeautifulSoup
import uuid

# Initialize ChromaDB
# We use a persistent client so data is saved to disk
CHROMA_DATA_PATH = "data/chroma_db"
os.makedirs(CHROMA_DATA_PATH, exist_ok=True)

client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)

# Use a standard lightweight model for embeddings
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Get or create the collection
collection = client.get_or_create_collection(name="qa_agent_docs", embedding_function=sentence_transformer_ef)

def parse_file(file_path: str) -> str:
    """Extracts text content from various file types."""
    ext = os.path.splitext(file_path)[1].lower()
    content = ""
    
    try:
        if ext == ".pdf":
            doc = fitz.open(file_path)
            for page in doc:
                content += page.get_text()
        elif ext == ".html":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                soup = BeautifulSoup(f, "html.parser")
                content = soup.get_text(separator="\n")
        elif ext == ".json":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
                content = json.dumps(data, indent=2)
        else: # .txt, .md, etc.
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return ""
        
    return content

def parse_file_content(file_content: bytes, filename: str) -> str:
    """Extracts text content from file-like objects (e.g., Streamlit uploads)."""
    ext = os.path.splitext(filename)[1].lower()
    content = ""
    
    try:
        if ext == ".pdf":
            # PyMuPDF can open from bytes
            doc = fitz.open(stream=file_content, filetype="pdf")
            for page in doc:
                content += page.get_text()
            doc.close()
        elif ext == ".html":
            soup = BeautifulSoup(file_content.decode("utf-8", errors="ignore"), "html.parser")
            content = soup.get_text(separator="\n")
        elif ext == ".json":
            data = json.loads(file_content.decode("utf-8", errors="ignore"))
            content = json.dumps(data, indent=2)
        else: # .txt, .md, etc.
            content = file_content.decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Error parsing {filename}: {e}")
        return ""
        
    return content

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Simple overlapping chunker."""
    if not text:
        return []
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def ingest_documents(file_paths: List[str]) -> int:
    """
    Ingests a list of file paths into the ChromaDB collection.
    Returns the number of chunks added.
    """
    global collection
    
    chunks_to_add = []
    metadatas = []
    ids = []
    
    for path in file_paths:
        content = parse_file(path)
        if not content:
            continue
            
        file_chunks = chunk_text(content)
        
        for i, chunk in enumerate(file_chunks):
            chunks_to_add.append(chunk)
            metadatas.append({
                "source": os.path.basename(path),
                "chunk_index": i
            })
            ids.append(f"{os.path.basename(path)}_{i}_{uuid.uuid4()}")
            
    if chunks_to_add:
        collection.add(
            documents=chunks_to_add,
            metadatas=metadatas,
            ids=ids
        )
        
    return len(chunks_to_add)

def ingest_uploaded_files(uploaded_files: List[tuple]) -> int:
    """
    Ingests Streamlit uploaded files (file-like objects) into the ChromaDB collection.
    Args:
        uploaded_files: List of tuples (filename, file_content_bytes)
    Returns the number of chunks added.
    """
    global collection
    
    chunks_to_add = []
    metadatas = []
    ids = []
    
    for filename, file_content in uploaded_files:
        content = parse_file_content(file_content, filename)
        if not content:
            continue
            
        file_chunks = chunk_text(content)
        
        for i, chunk in enumerate(file_chunks):
            chunks_to_add.append(chunk)
            metadatas.append({
                "source": filename,
                "chunk_index": i
            })
            ids.append(f"{filename}_{i}_{uuid.uuid4()}")
            
    if chunks_to_add:
        collection.add(
            documents=chunks_to_add,
            metadatas=metadatas,
            ids=ids
        )
        
    return len(chunks_to_add)

def clear_knowledge_base():
    """Clears the ChromaDB collection."""
    global collection
    try:
        client.delete_collection(name="qa_agent_docs")
        collection = client.get_or_create_collection(name="qa_agent_docs", embedding_function=sentence_transformer_ef)
    except Exception as e:
        print(f"Error clearing knowledge base: {e}")

def get_knowledge_base():
    """Returns the collection (for debugging or direct access if needed)."""
    return collection
