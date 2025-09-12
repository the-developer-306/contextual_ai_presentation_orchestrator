from langchain.vectorstores import Chroma
import os

def build_vectorstore(split_docs, embeddings, persist_directory="vector_db"):
    """Build or update Chroma vector store."""
    os.makedirs(persist_directory, exist_ok=True)
    vectorstore = Chroma.from_documents(
        documents=split_docs,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    vectorstore.persist()
    return vectorstore

def load_vectorstore(embeddings, persist_directory="vector_db"):
    """Load an existing Chroma vector store."""
    return Chroma(
        embedding_function=embeddings,
        persist_directory=persist_directory
    )
