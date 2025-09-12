from rag_pipeline.loaders import load_documents
from rag_pipeline.splitter import split_documents
from rag_pipeline.embeddings import get_embeddings
from rag_pipeline.vector_store import build_vectorstore, load_vectorstore
from rag_pipeline.retriever import get_retriever, retrieve_with_citations

class RAGPipeline:
    def __init__(self, persist_directory="vector_db"):
        self.persist_directory = persist_directory
        self.embeddings = get_embeddings()
        self.vectorstore = None
        self.retriever = None

    def build(self, file_paths):
        docs = load_documents(file_paths)
        split_docs = split_documents(docs)
        self.vectorstore = build_vectorstore(split_docs, self.embeddings, self.persist_directory)
        self.retriever = get_retriever(self.vectorstore)
        return self

    def load(self):
        self.vectorstore = load_vectorstore(self.embeddings, self.persist_directory)
        self.retriever = get_retriever(self.vectorstore)
        return self

    def query(self, question, k=5):
        return retrieve_with_citations(self.retriever, question)
