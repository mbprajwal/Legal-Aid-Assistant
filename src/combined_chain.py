# src/combined_chain.py

import re
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

from src.retriever import build_retriever
from src.memory_chain import MemoryChatbot
from src.document_chain import DocumentGeneratorChain
from src.document_intent import detect_document_intent


# ---------------------------------------------------------
# Load LLM
# ---------------------------------------------------------
def load_llm(model_name="llama2"):
    return ChatOllama(
        model=model_name,
        temperature=0.2,
        max_tokens=200
    )


# ---------------------------------------------------------
# SYSTEM PROMPT
# ---------------------------------------------------------
SYSTEM_PROMPT = """
You are a concise Indian legal assistant.

Rules:
- Respond in 1–2 factual sentences.
- Do not greet.
- Do not repeat yourself.
- Do not hallucinate.
- Use memory only for personal questions about the user.
- Use retrieved context only for legal questions.
- If unsure, say: "I do not have information about that."
"""


# ---------------------------------------------------------
# PROMPT TEMPLATE
# ---------------------------------------------------------
prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("system", "Known user facts:\n{memory}"),
    ("system", "Legal context:\n{context}"),
    ("system", "Conversation:\n{history}"),
    ("user", "{query}")
])


# ---------------------------------------------------------
# Intent Classification
# ---------------------------------------------------------
PERSONAL_PATTERNS = [
    r"my name",
    r"who am i",
    r"where do i live",
    r"i live",
    r"i am a",
    r"what do i do",
    r"what is my",
]

LEGAL_PATTERNS = [
    r"dispute",
    r"rights",
    r"law",
    r"illegal",
    r"how to file",
    r"fir",
    r"rti",
    r"tenant",
    r"harassment",
    r"police",
]


def is_legal_query(q):
    q = q.lower()
    return any(re.search(p, q) for p in LEGAL_PATTERNS)


# ---------------------------------------------------------
# Combined Chatbot
# ---------------------------------------------------------
class CombinedLegalChatbot:
    def __init__(self, model_name="llama2"):
        self.llm = load_llm(model_name)
        self.retriever = build_retriever(5)
        self.memory = MemoryChatbot()
        self.doc_gen = DocumentGeneratorChain()

    # -----------------------------------------------------
    def _get_memory_string(self):
        if not self.memory.memory_store:
            return "None"
        return "\n".join(f"- {k}: {v}" for k, v in self.memory.memory_store.items())

    # -----------------------------------------------------
    def _summarize_history(self):
        msgs = self.memory.history.messages[-6:]
        out = []
        for m in msgs:
            if m.type == "human":
                out.append("User: " + m.content)
            else:
                out.append("Assistant: " + m.content)
        return "\n".join(out)

    # -----------------------------------------------------
    def _retrieve_context(self, user_query):
        """Use RAG ONLY for legal queries."""
        if not is_legal_query(user_query):
            return "None"

        docs = self.retriever.invoke(user_query)
        if docs:
            return "\n---\n".join([d.page_content for d in docs])
        return "None"

    # -----------------------------------------------------
    # 🔥 Document Generation Handler
    # -----------------------------------------------------
    def _handle_document_flow(self, user_query, template_name):
        """Handles FIR / RTI / Notice / Complaint generation."""

        template = self.doc_gen.load_template(template_name)

        print(f"\n--- Document Required: {template['title']} ---")

        # Autofill from memory
        autofilled = {}
        for field_key, field_label in template["fields"].items():
            autofilled[field_key] = (
                self.memory.get_fact(field_key)
                or ""  # if memory does not have value
            )

        # Ask user for missing values
        print("Provide the following details:")
        for field_key, field_label in template["fields"].items():
            if not autofilled[field_key]:
                value = input(f"{field_label}: ").strip()
                autofilled[field_key] = value

        # Retrieve RAG context
        docs = self.retriever.invoke(user_query)
        context = "\n---\n".join([d.page_content for d in docs]) or "None"

        # Generate document draft
        draft = self.doc_gen.generate_document(
            template_name=template_name,
            user_inputs=autofilled,
            memory_string=self._get_memory_string(),
            rag_context=context,
        )

        return (
            f"\n📄 **Draft generated for: {template['title']}**\n\n"
            f"{draft}\n\n"
            "You may now save/export it to PDF."
        )

    # -----------------------------------------------------
    # MAIN GENERATE FUNCTION
    # -----------------------------------------------------
    def generate(self, user_query):

        # 0️⃣ Detect document request
        doc_template = detect_document_intent(user_query)
        

        if doc_template:
            return self._handle_document_flow(user_query, doc_template)

        # 1️⃣ Update memory
        self.memory.add_user_message(user_query)

        # 2️⃣ RAG context if legal
        context = self._retrieve_context(user_query)

        # 3️⃣ Build final prompt
        prompt = prompt_template.invoke({
            "memory": self._get_memory_string(),
            "context": context,
            "history": self._summarize_history(),
            "query": user_query
        })

        # 4️⃣ Generate answer
        response = self.llm.invoke(prompt).content.strip()

        # 5️⃣ Save assistant reply in memory
        self.memory.add_assistant_response(response)

        return response
