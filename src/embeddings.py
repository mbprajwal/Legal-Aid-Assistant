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
    Loads your local MiniLM sentence-transformer model.
    Edit path below if you move the model folder.
    """
    return LocalSentenceTransformerEmbeddings(model_path=MODEL_PATH)
