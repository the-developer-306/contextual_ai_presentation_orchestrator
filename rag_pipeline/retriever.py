def get_retriever(vectorstore, k=5):
    """Return retriever with top-k relevant chunks."""
    return vectorstore.as_retriever(search_type="similarity", k=k)

def retrieve_with_citations(retriever, query):
    """Retrieve chunks with sources for citation tracking."""
    results = retriever.get_relevant_documents(query)
    citations = [
        {"content": doc.page_content, "source": doc.metadata.get("source", "Unknown")}
        for doc in results
    ]
    return citations
