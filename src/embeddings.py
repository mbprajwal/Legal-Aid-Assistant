# src/embeddings.py
"""
Embeddings module for LangChain-based Legal Aid System.
Uses a LOCAL SentenceTransformer model (MiniLM) for consistent RAG performance.
"""

import os
from sentence_transformers import SentenceTransformer
from langchain.embeddings.base import Embeddings
from dotenv import load_dotenv

load_dotenv()
MODEL_PATH = os.getenv("MODEL_PATH")

class LocalSentenceTransformerEmbeddings(Embeddings):
    """
    LangChain-compatible wrapper for your local SentenceTransformer model.
    """

    def __init__(self, model_path: str):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Embedding model not found at: {model_path}")

        print(f"🔧 Loading embeddings model from: {model_path}")
        self.model = SentenceTransformer(model_path)

    def embed_documents(self, texts):
        """
        Embed multiple documents → returns list of vectors.
        """
        return self.model.encode(texts, show_progress_bar=False).tolist()

    def embed_query(self, text):
        """
        Embed a single query → returns a vector.
        """
        return self.model.encode(text, show_progress_bar=False).tolist()


# ---------------------------------------------------------
# Utility function to load embeddings (used across project)
# ---------------------------------------------------------

def load_embedding_model():
    """
    Loads the sentence transformer model.
    If local path exists, use it. Otherwise, use a default HuggingFace model.
    """
    if MODEL_PATH and os.path.exists(MODEL_PATH):
        return LocalSentenceTransformerEmbeddings(model_path=MODEL_PATH)
    
    print(f"Local model not found at {MODEL_PATH}. Using default HuggingFace model: all-MiniLM-L6-v2")
    from langchain_community.embeddings import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
