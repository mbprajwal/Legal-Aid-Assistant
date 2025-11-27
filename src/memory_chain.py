# # src/memory_chain.py

# import os
# from dotenv import load_dotenv

# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_core.messages import HumanMessage, AIMessage
# from langchain_core.runnables import RunnablePassthrough

# from langchain_ollama import OllamaLLM
# from langchain_community.chat_message_histories import ChatMessageHistory

# load_dotenv()

# class MemoryChatbot:
#     """
#     Legal chatbot with conversation memory using LangChain v1.
#     Responses are concise, professional, and one-line only.
#     """

#     def __init__(self, model_name="llama2"):
#         self.llm = OllamaLLM(model=model_name)
#         self.memory_store = {}
#         # true conversation memory
#         self.history = ChatMessageHistory()

#         # strict concise legal prompt
#         self.prompt = ChatPromptTemplate.from_messages([
#             ("system",
#             """You are a concise and professional Indian legal assistant.
# - Respond in ONE line only.
# - Greet the user in the first message only, no need to greet again in the subsequent messages.
# - Do NOT use emojis, jokes, or emotional tone.
# - Do NOT repeat phrases like "as your legal assistant".
# - Only use user's memory when relevant.
# - Never invent personal details; only recall what user told you.
# - Keep the answer formal and neutral."""
#             ),
#             MessagesPlaceholder(variable_name="chat_history"),
#             ("human", "{question}")
#         ])

#         # memory → prompt → llm
#         self.chain = (
#             {
#                 "chat_history": lambda _: self.history.messages,
#                 "question": RunnablePassthrough()
#             }
#             | self.prompt
#             | self.llm
#         )

#     def ask(self, query: str):
#         """Ask a question with memory + print user message for debugging."""

#         print(f"\nUSER: {query}")  # print before answering

#         # Save user message
#         self.history.add_message(HumanMessage(content=query))

#         # Generate
#         response = self.chain.invoke(query)

#         # Save assistant message
#         self.history.add_message(AIMessage(content=response))

#         # print(f"ASSISTANT: {response}")  # print output cleanly

#         return response
    
#     def add_user_message(self, text: str):
#         """External modules can push user messages into memory."""
#         self.history.add_message(HumanMessage(content=text))


#     def add_assistant_response(self, text: str):
#         """External modules can push assistant replies into memory."""
#         self.history.add_message(AIMessage(content=text))

#     def get_memory(self):
#         return self.history.messages

#     def process_user_message(self, user_message: str):
#         """
#         Required by combined_chain.py.
#         - Stores the user message
#         - Generates a compact memory snippet relevant to the question
#         """
#         # Save user message into history
#         self.history.add_message(HumanMessage(content=user_message))

#         # Build a summarization prompt to compress memory → useful for RAG
#         summarize_prompt = f"""
# Summarize only the important personal facts the user has shared so far.
# Do NOT add anything new.
# Keep summary extremely short (1-2 lines).
# Conversation:
# {[m.content for m in self.history.messages]}
# """

#         try:
#             summary = self.llm.invoke(summarize_prompt).strip()
#         except Exception:
#             summary = ""  # fail-safe

#         if summary:
#             key = f"memory_{len(self.memory_store)}"
#             self.memory_store[key] = summary
#         return self.memory_store

#     def get_fact(self, key):
#         return self.memory_store.get(key)


# src/memory_chain.py

import re
import json
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_ollama import ChatOllama


class MemoryChatbot:
    """
    Hybrid memory:
    - Regex-based extraction for known common facts
    - LLM-based extraction for all other arbitrary facts
    """

    def __init__(self):
        self.history = ChatMessageHistory()
        self.memory_store = {}  # fully flexible key-value memory
        self.llm = ChatOllama(model="llama2", temperature=0)

        # Known patterns → stored directly
        self.regex_patterns = {
            "name": [
                r"my name is ([a-zA-Z ]+)",
            ],
            "location": [
                r"i live in ([a-zA-Z ]]+)",
                r"i am from ([a-zA-Z ]]+)",
            ],
            "age": [
                r"i am (\d{1,2}) years old",
                r"my age is (\d{1,2})"
            ],
            "occupation": [
                r"i work as ([a-zA-Z ]+)",
                r"i am a ([a-zA-Z ]+)"
            ],
            "phone": [
                r"my phone number is (\d{10})",
            ],
            "email": [
                r"my email is ([^\s@]+@[^\s@]+)"
            ]
        }


    # -------------------------------------------------------------------
    # Main interface
    # -------------------------------------------------------------------
    def add_user_message(self, text: str):
        self.history.add_message(HumanMessage(content=text))
        self._extract_facts(text)


    def add_assistant_response(self, text: str):
        self.history.add_message(AIMessage(content=text))


    def get_fact(self, key: str):
        return self.memory_store.get(key)


    def get_memory_string(self):
        if not self.memory_store:
            return "None"

        return "\n".join(f"{k}: {v}" for k, v in self.memory_store.items())
    def get_history(self):
        """
        Return the raw list of chat message objects (compatible with older code).
        Each item has .type and .content attributes.
        """
        return self.history.messages

    # -------------------------------------------------------------------
    # Extraction logic (Regex first → LLM fallback)
    # -------------------------------------------------------------------
    def _extract_facts(self, text: str):
        text_lower = text.lower()

        # 1. Check regex patterns first
        for field, patterns in self.regex_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    value = match.group(1).strip()
                    self.memory_store[field] = value
                    return  # stop once matched

        # 2. LLM fallback: detect arbitrary facts
        extracted = self._extract_fact_llm(text)
        if extracted:
            key = extracted.get("key")
            value = extracted.get("value")
            if key and value:
                self.memory_store[key] = value


    def _extract_fact_llm(self, message: str):
        """
        Use LLM to extract arbitrary personal facts such as:
        - my father's name is X
        - my college is Y
        - my landlord is Z
        """
        prompt = f"""
Extract ONE personal fact from this sentence only if it clearly states a fact.

Return strict JSON:
{{
  "key": "<field_name_in_snake_case>",
  "value": "<value>"
}}

If no fact present, return:
{{}}
        
Sentence:
"{message}"
"""

        try:
            response = self.llm.invoke(prompt).content.strip()
            data = json.loads(response)
            return data
        except:
            return {}
