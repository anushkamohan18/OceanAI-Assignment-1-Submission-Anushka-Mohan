import os
from typing import List

# Global in-memory store
# List of {"source": str, "content": str}
KNOWLEDGE_BASE = []

def get_knowledge_base():
    return KNOWLEDGE_BASE

def ingest_documents(file_paths: List[str]):
    """
    Ingests a list of file paths into the in-memory store.
    """
    global KNOWLEDGE_BASE
    chunks_count = 0
    
    for path in file_paths:
        try:
            content = ""
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            # Simple chunking: split by double newlines or just keep as one big chunk if small
            # For this assignment, files are small, so maybe 1000 chars chunks
            
            # Create chunks
            chunk_size = 1000
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i+chunk_size]
                KNOWLEDGE_BASE.append({
                    "source": os.path.basename(path),
                    "content": chunk
                })
                chunks_count += 1
                
        except Exception as e:
            print(f"Error reading {path}: {e}")
            
    return chunks_count

def clear_knowledge_base():
    global KNOWLEDGE_BASE
    KNOWLEDGE_BASE = []
