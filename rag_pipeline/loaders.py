import os
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader

def load_documents(file_paths: list):
    """Load PDFs, DOCX, TXT, MD into LangChain Document objects."""
    documents = []
    for path in file_paths:
        ext = os.path.splitext(path)[1].lower()
        if ext == ".pdf":
            loader = PyPDFLoader(path)
        elif ext == ".docx":
            loader = Docx2txtLoader(path)
        elif ext == ".txt" or ext == ".md":
            loader = TextLoader(path)
        else:
            print(f" Skipping unsupported file: {path}")
            continue
        documents.extend(loader.load())
    return documents
