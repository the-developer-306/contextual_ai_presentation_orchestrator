from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
import os
import shutil
from rag_pipeline.pipeline import RAGPipeline
from utils.security import require_role

router = APIRouter(tags=["Upload"])

UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Define allowed MIME types
ALLOWED_MIME_TYPES = {
    "text/plain",  # TXT
    "text/markdown",  # MD
    "application/pdf",  # PDF
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # DOCX
}

@router.post("/upload-doc")
async def upload_docs(
    files: list[UploadFile] = File(...),
    user=Depends(require_role(["Executive", "Senior Manager", "Analyst"]))
):
    """
    Upload files and index into RAG. Returns saved file paths and user info.
    """
    
    # print("UPLOAD ENDPOINT CALLED  with user:", user)
    # print("FILES RECEIVED:", [f.filename for f in files])
    
    try:
        # Validate file types
        for file in files:
            if file.content_type not in ALLOWED_MIME_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"File type {file.content_type} not allowed. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}"
                )
        
        saved_files = []
        for file in files:
            # Ensure file has content
            if file.size == 0:
                raise HTTPException(status_code=400, detail=f"File {file.filename} is empty")
                
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            file_path = os.path.normpath(file_path)  # prevent path traversal
            
            # Save file
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            saved_files.append(file_path)

        # Index into vector DB
        rag = RAGPipeline(persist_directory="vector_db")
        if hasattr(rag, "index_documents"):
            rag.index_documents(saved_files)
        elif hasattr(rag, "build"):
            rag.build(saved_files)
        elif hasattr(rag, "create_vectorstore") and callable(getattr(rag, "create_vectorstore")):
            rag.create_vectorstore(saved_files)

        return {
            "message": " Documents uploaded & processed",
            "files": saved_files,
            "user": user
        }
    except Exception as e:
        print(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")
