# src/retriever.py
"""
Retriever module for LangChain-based Legal Aid System.
Uses:
- Pinecone v5/v7 client
- langchain-pinecone wrapper
"""

import os
from dotenv import load_dotenv

from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore

from src.embeddings import load_embedding_model


# ---------------------------------------------------------
# Initialize Pinecone client
# ---------------------------------------------------------
def init_pinecone():
    load_dotenv()

    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME", "legalaid2")

    if not api_key:
        raise ValueError("❌ Missing PINECONE_API_KEY in .env")

    pc = Pinecone(api_key=api_key)

    # get list of indexes
    existing = pc.list_indexes().names()

    if index_name not in existing:
        raise ValueError(
            f"❌ Pinecone index '{index_name}' does NOT exist.\n"
            f"➡ Create it first or load the correct index name."
        )

    # v5/v7: index is fetched using .Index()
    index = pc.Index(index_name)

    print(f"📦 Connected to Pinecone index: {index_name}")
    return index


# ---------------------------------------------------------
# Build LangChain Retriever
# ---------------------------------------------------------
def build_retriever(top_k: int = 5):
    """
    Creates a LangChain retriever using:
    - local embeddings
    - Pinecone vector index
    - cosine similarity search
    """

    embeddings = load_embedding_model()
    index = init_pinecone()

    # langchain-pinecone wrapper
    vectorstore = PineconeVectorStore(
        index=index,
        embedding=embeddings,
        text_key="text",      # must match metadata key you used during upsert
        namespace=None        # set if you used namespace
    )

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": top_k}
    )

    print("🔎 Retriever initialized using langchain-pinecone.")
    return retriever
