from langchain.embeddings import HuggingFaceEmbeddings

def get_embeddings():
    """Return a Sentence Transformer embedding model."""
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
