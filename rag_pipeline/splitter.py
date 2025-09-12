from langchain.text_splitter import RecursiveCharacterTextSplitter

def split_documents(docs, chunk_size=800, chunk_overlap=150):
    """Split docs into overlapping chunks for better embeddings."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(docs)
