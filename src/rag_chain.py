# src/rag_chain.py

import os
from dotenv import load_dotenv

from langchain_ollama import OllamaLLM
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.prompts import PromptTemplate

from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from pinecone import Pinecone


load_dotenv()

class RAGChatbot:
    def __init__(self):
        # --- Embeddings ---
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # --- Pinecone ---
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index_name = os.getenv("PINECONE_INDEX_NAME")
        self.vectorstore = PineconeVectorStore(
            index_name=index_name,
            embedding=self.embeddings
        )

        # --- LLM (Ollama) ---
        self.llm = OllamaLLM(model="llama2")

        # --- Prompt ---
        self.prompt = PromptTemplate(
            template="""
You are an Indian legal assistant.

Context:
{context}

Question:
{question}

Answer clearly, politely, and only using the provided context.
""",
            input_variables=["context", "question"]
        )

        # --- RAG Chain (NEW API) ---
        self.chain = (
            {
                "context": self.vectorstore.as_retriever(),
                "question": RunnablePassthrough()
            }
            | self.prompt
            | self.llm
        )

    def ask(self, query: str):
        """Run RAG query."""
        return self.chain.invoke(query)
