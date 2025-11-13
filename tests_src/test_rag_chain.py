# test_rag_chain.py
# this file was used to test the RAGChatbot class from the rag_chain.py file
import os, sys
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

from src.rag_chain import RAGChatbot

bot = RAGChatbot()
response = bot.ask("What is a plaint and how is it filed?")
print("\nBot Response:\n", response)
