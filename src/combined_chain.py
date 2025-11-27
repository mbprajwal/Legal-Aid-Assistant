# # src/combined_chain.py

# import re
# from langchain_ollama import ChatOllama
# from langchain_core.prompts import ChatPromptTemplate

# from src.retriever import build_retriever
# from src.memory_chain import MemoryChatbot
# from src.document_chain import DocumentGeneratorChain
# from src.document_intent import detect_document_intent


# # ---------------------------------------------------------
# # Load LLM
# # ---------------------------------------------------------
# def load_llm(model_name="llama2"):
#     return ChatOllama(
#         model=model_name,
#         temperature=0.2,
#         max_tokens=200
#     )


# # ---------------------------------------------------------
# # SYSTEM PROMPT
# # ---------------------------------------------------------
# SYSTEM_PROMPT = """
# You are a concise Indian legal assistant.

# Rules:
# - Respond in 1–2 factual sentences.
# - If the user greets, greet back.
# - Do not repeat yourself.
# - Do not hallucinate.
# - Use memory only for personal questions about the user.
# - Use retrieved context only for legal questions.
# - If unsure, say: "I do not have information about that."
# """


# # ---------------------------------------------------------
# # PROMPT TEMPLATE
# # ---------------------------------------------------------
# prompt_template = ChatPromptTemplate.from_messages([
#     ("system", SYSTEM_PROMPT),
#     ("system", "Known user facts:\n{memory}"),
#     ("system", "Legal context:\n{context}"),
#     ("system", "Conversation:\n{history}"),
#     ("user", "{query}")
# ])


# # ---------------------------------------------------------
# # Intent Classification
# # ---------------------------------------------------------
# PERSONAL_PATTERNS = [
#     r"my name",
#     r"who am i",
#     r"where do i live",
#     r"i live",
#     r"i am a",
#     r"what do i do",
#     r"what is my",
# ]

# LEGAL_PATTERNS = [
#     r"dispute",
#     r"rights",
#     r"law",
#     r"illegal",
#     r"how to file",
#     r"fir",
#     r"rti",
#     r"tenant",
#     r"harassment",
#     r"police",
# ]


# def is_legal_query(q):
#     q = q.lower()
#     return any(re.search(p, q) for p in LEGAL_PATTERNS)


# # ---------------------------------------------------------
# # Combined Chatbot
# # ---------------------------------------------------------
# class CombinedLegalChatbot:
#     def __init__(self, model_name="llama2"):
#         self.llm = load_llm(model_name)
#         self.retriever = build_retriever(5)
#         self.memory = MemoryChatbot()
#         self.doc_gen = DocumentGeneratorChain()

#     # -----------------------------------------------------
#     def _get_memory_string(self):
#         if not self.memory.memory_store:
#             return "None"
#         return "\n".join(f"- {k}: {v}" for k, v in self.memory.memory_store.items())

#     # -----------------------------------------------------
#     def _summarize_history(self):
#         msgs = self.memory.history.messages[-6:]
#         out = []
#         for m in msgs:
#             if m.type == "human":
#                 out.append("User: " + m.content)
#             else:
#                 out.append("Assistant: " + m.content)
#         return "\n".join(out)

#     # -----------------------------------------------------
#     def _retrieve_context(self, user_query):
#         """Use RAG ONLY for legal queries."""
#         if not is_legal_query(user_query):
#             return "None"

#         docs = self.retriever.invoke(user_query)
#         if docs:
#             return "\n---\n".join([d.page_content for d in docs])
#         return "None"

#     # -----------------------------------------------------
#     # 🔥 Document Generation Handler
#     # -----------------------------------------------------
#     def _handle_document_flow(self, user_query, template_name):
#         """Handles FIR / RTI / Notice / Complaint generation."""

#         template = self.doc_gen.load_template(template_name)

#         print(f"\n--- Document Required: {template['title']} ---")

#         # Autofill from memory
#         autofilled = {}
#         for field_key, field_label in template["fields"].items():
#             autofilled[field_key] = (
#                 self.memory.get_fact(field_key)
#                 or ""  # if memory does not have value
#             )

#         # Ask user for missing values
#         print("Provide the following details:")
#         for field_key, field_label in template["fields"].items():
#             if not autofilled[field_key]:
#                 value = input(f"{field_label}: ").strip()
#                 autofilled[field_key] = value

#         # Retrieve RAG context
#         docs = self.retriever.invoke(user_query)
#         context = "\n---\n".join([d.page_content for d in docs]) or "None"

#         # Generate document draft
#         draft = self.doc_gen.generate_document(
#             template_name=template_name,
#             user_inputs=autofilled,
#             memory_string=self._get_memory_string(),
#             rag_context=context,
#         )

#         return (
#             f"\n📄 **Draft generated for: {template['title']}**\n\n"
#             f"{draft}\n\n"
#             "You may now save/export it to PDF."
#         )

#     # -----------------------------------------------------
#     # MAIN GENERATE FUNCTION
#     # -----------------------------------------------------
#     def generate(self, user_query):

#         # 0️⃣ Detect document request
#         doc_template = detect_document_intent(user_query)
        

#         if doc_template:
#             return self._handle_document_flow(user_query, doc_template)

#         # 1️⃣ Update memory
#         self.memory.add_user_message(user_query)

#         # 2️⃣ RAG context if legal
#         context = self._retrieve_context(user_query)

#         # 3️⃣ Build final prompt
#         prompt = prompt_template.invoke({
#             "memory": self._get_memory_string(),
#             "context": context,
#             "history": self._summarize_history(),
#             "query": user_query
#         })

#         # 4️⃣ Generate answer
#         response = self.llm.invoke(prompt).content.strip()

#         # 5️⃣ Save assistant reply in memory
#         self.memory.add_assistant_response(response)

#         return response

# src/combined_chain.py
# src/combined_chain.py

import re
from typing import Optional

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
- If the user greets, greet back.
- Use memory ONLY for personal questions.
- Use RAG ONLY for legal questions.
- Never hallucinate missing facts.
- If unsure, say: "I do not have information about that."
- Do NOT repeat yourself.
"""


# ---------------------------------------------------------
# PROMPT TEMPLATE
# ---------------------------------------------------------
prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("system", "Known user personal facts:\n{memory}"),
    ("system", "Relevant legal context:\n{context}"),
    ("system", "Conversation history:\n{history}"),
    ("user", "{query}")
])


# ---------------------------------------------------------
# CombinedLegalChatbot with:
# - Flexible Memory
# - Personal Question Handler
# - Document State Machine
# - Clean RAG Routing
# ---------------------------------------------------------
class CombinedLegalChatbot:
    def __init__(self, model_name="llama2"):

        self.llm = load_llm(model_name)
        self.retriever = build_retriever(5)

        self.memory = MemoryChatbot()
        self.doc_gen = DocumentGeneratorChain()

        # Document state
        self.active_document: Optional[str] = None
        self.document_fields = {}
        self.document_field_order = []
        self.current_field_index = 0

        self.CANCEL_WORDS = {"cancel", "stop", "exit", "quit"}

    # ---------------------------------------------------------
    # Memory Helpers
    # ---------------------------------------------------------
    def _get_memory_string(self):
        return self.memory.get_memory_string()

    def _summarize_history(self):
        msgs = self.memory.get_history()
        msgs = msgs[-6:]
        lines = []
        for m in msgs:
            prefix = "User" if m.type == "human" else "Assistant"
            lines.append(f"{prefix}: {m.content}")
        return "\n".join(lines) if lines else "None"

    # ---------------------------------------------------------
    # PERSONAL QUESTION HANDLER (Direct Output)
    # ---------------------------------------------------------
    def _answer_personal_query(self, query: str):
        q = query.lower()

        patterns = {
            "name": [r"what is my name", r"who am i"],
            "father_name": [r"father name", r"dad name", r"my father"],
            "location": [r"where do i live", r"my location"],
            "age": [r"what is my age", r"how old am i"],
            "occupation": [r"my occupation", r"what do i do"],
            "phone": [r"my phone"],
            "email": [r"my email"],
        }

        for key, pats in patterns.items():
            for p in pats:
                if re.search(p, q):
                    val = self.memory.get_fact(key)
                    if val:
                        key_clean = key.replace("_", " ")
                        return f"Your {key_clean} is {val}."
                    else:
                        return f"I do not have your {key.replace('_', ' ')} in my memory yet."

        return None

    # ---------------------------------------------------------
    # DOCUMENT STATE MACHINE
    # ---------------------------------------------------------
    def start_document_flow(self, template_name: str):
        template = self.doc_gen.load_template(template_name)

        self.active_document = template_name
        self.document_fields = {k: "" for k in template["fields"].keys()}
        self.document_field_order = list(template["fields"].keys())
        self.current_field_index = 0

        # Autofill using memory
        for key in self.document_fields:
            val = self.memory.get_fact(key)
            if val:
                self.document_fields[key] = val

        intro = f"Okay, let's fill your {template['title']}. Say 'cancel' anytime."
        first_q = self.ask_next_field()
        return f"{intro}\n\n{first_q}"

    def ask_next_field(self):
        template = self.doc_gen.load_template(self.active_document)
        field_labels = template["fields"]

        while self.current_field_index < len(self.document_field_order):
            key = self.document_field_order[self.current_field_index]
            if not self.document_fields[key]:
                return f"{field_labels[key]}?"
            self.current_field_index += 1

        return None

    def handle_document_answer(self, user_msg: str):
        if user_msg.lower() in self.CANCEL_WORDS:
            self._clear_document_state()
            return "Document filling cancelled."

        key = self.document_field_order[self.current_field_index]
        text = user_msg.strip()

        if text.lower() in {"skip", "none"}:
            self.document_fields[key] = "[missing]"
        else:
            self.document_fields[key] = text

        self.current_field_index += 1
        nxt = self.ask_next_field()

        if nxt:
            return nxt

        final_template = self.active_document
        memory_text = self._get_memory_string()

        self._clear_document_state()

        draft = self.doc_gen.generate_document(
            template_name=final_template,
            user_inputs=self.document_fields,
            memory_string=memory_text,
            rag_context="None"
        )

        return f"📄 **Your legal draft is ready:**\n\n{draft}"

    def _clear_document_state(self):
        self.active_document = None
        self.document_fields = {}
        self.document_field_order = []
        self.current_field_index = 0

    # ---------------------------------------------------------
    # RAG Filtering
    # ---------------------------------------------------------
    def _is_personal_query(self, text):
        markers = ["my ", "i am", "who am i", "what is my", "where do i"]
        return any(m in text.lower() for m in markers)

    def _is_legal_query(self, text):
        markers = [
            "law", "illegal", "rights", "court",
            "fir", "rti", "police", "tenant",
            "harassment", "complaint"
        ]
        return any(m in text.lower() for m in markers)

    def _retrieve_context(self, user_query):
        if self.active_document:
            return "None"
        if self._is_personal_query(user_query):
            return "None"
        if not self._is_legal_query(user_query):
            return "None"

        try:
            docs = self.retriever.invoke(user_query)
            if docs:
                return "\n---\n".join(d.page_content for d in docs)
        except:
            return "None"

        return "None"

    # ---------------------------------------------------------
    # MAIN CHAT LOOP
    # ---------------------------------------------------------
    def generate(self, user_query: str):

        # 0️⃣ Document flow
        if self.active_document:
            return self.handle_document_answer(user_query)

        # 1️⃣ Document intent (create FIR, RTI, etc.)
        doc_template = detect_document_intent(user_query)
        if doc_template:
            return self.start_document_flow(doc_template)

        # 2️⃣ DIRECT PERSONAL MEMORY ANSWER
        personal_answer = self._answer_personal_query(user_query)
        if personal_answer:
            self.memory.add_user_message(user_query)
            self.memory.add_assistant_response(personal_answer)
            return personal_answer

        # 3️⃣ Add user info to memory (extract facts)
        self.memory.add_user_message(user_query)

        # 4️⃣ RAG if legal
        rag_context = self._retrieve_context(user_query)

        # 5️⃣ Build final prompt
        prompt = prompt_template.invoke({
            "memory": self._get_memory_string(),
            "context": rag_context,
            "history": self._summarize_history(),
            "query": user_query
        })

        # 6️⃣ Generate reply
        response = self.llm.invoke(prompt).content.strip()

        # 7️⃣ Store assistant reply
        self.memory.add_assistant_response(response)

        return response


