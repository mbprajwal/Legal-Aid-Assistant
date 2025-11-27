# tests_src/test_document.py

import os
import sys

# Ensure project root is in path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT)

from src.document_chain import DocumentGeneratorChain
from src.combined_chain import CombinedLegalChatbot

# ------------------------------------------------------------
# 1) Initialize chatbot + document generator
# ------------------------------------------------------------
bot = CombinedLegalChatbot()
doc_gen = DocumentGeneratorChain()

# ------------------------------------------------------------
# 2) Simulate short conversation to store memory
# ------------------------------------------------------------
bot.generate("My name is Ramesh")
bot.generate("I live in Mysuru")
bot.generate("I am a daily wage worker")

# ------------------------------------------------------------
# 3) User requests an FIR document
# ------------------------------------------------------------
user_query = "I want to file an FIR for a theft incident."

# Extract memory
memory_str = bot._get_memory_string()

# Retrieve legal context (RAG)
docs = bot.retriever.invoke(user_query)
rag_context = "\n".join([d.page_content for d in docs]) or "None"

# ------------------------------------------------------------
# 4) Fill template fields
# ------------------------------------------------------------
user_inputs = {
    "name": "Ramesh",
    "address": "Mysuru",
    "date": "2025-01-10",
    "details": "My phone was stolen while waiting at the bus stop, I could partially notice the theif's clothes, he was wearing a black shirt and a blue jeans, he had his face covered with a mask and looked a bit lean."
}

# ------------------------------------------------------------
# 5) Generate document draft
# ------------------------------------------------------------
draft_text = doc_gen.generate_document(
    template_name="fir",
    user_inputs=user_inputs,
    memory_string=memory_str,
    rag_context=rag_context
)

print("\n========== GENERATED DOCUMENT ==========\n")
print(draft_text)
print("\n========================================\n")

# ------------------------------------------------------------
# 6) Save PDF
# ------------------------------------------------------------
pdf_path = doc_gen.save_pdf(draft_text, "fir_output.pdf")
print("PDF saved at:", pdf_path)
