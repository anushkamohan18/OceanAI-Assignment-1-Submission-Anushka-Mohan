import os
import shutil
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from .ingestion import ingest_documents, clear_knowledge_base
from .rag import generate_test_cases, generate_selenium_script
from .models import TestCaseRequest, TestCase, ScriptRequest, ScriptResponse

app = FastAPI(title="Autonomous QA Agent API")

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class IngestResponse(BaseModel):
    message: str
    chunks_processed: int

@app.post("/upload_files", response_model=IngestResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    file_paths = []
    # Clear previous knowledge base to keep it fresh for the demo
    clear_knowledge_base()
    
    # Clean upload dir
    for f in os.listdir(UPLOAD_DIR):
        os.remove(os.path.join(UPLOAD_DIR, f))

    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_paths.append(file_path)
    
    try:
        num_chunks = ingest_documents(file_paths)
        return {"message": "Knowledge Base Built Successfully", "chunks_processed": num_chunks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_test_cases", response_model=List[TestCase])
async def generate_tests(request: TestCaseRequest):
    return generate_test_cases(request.query)

@app.post("/generate_script", response_model=ScriptResponse)
async def generate_script(request: ScriptRequest):
    # If HTML content is not provided in request, try to find it in uploads
    html_content = request.html_content
    if not html_content:
        # Look for html file in uploads
        for f in os.listdir(UPLOAD_DIR):
            if f.endswith(".html"):
                with open(os.path.join(UPLOAD_DIR, f), "r", encoding="utf-8") as file:
                    html_content = file.read()
                break
    
    script = generate_selenium_script(request.test_case, html_content or "")
    return {"script_code": script}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
