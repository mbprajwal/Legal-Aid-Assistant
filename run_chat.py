# run_chat.py

import os, sys
from src.combined_chain import CombinedLegalChatbot

# Initialize chatbot
bot = CombinedLegalChatbot()

print("\n==============================")
print("   Legal Aid Assistant (CLI)")
print("==============================")
print("Type your queries below.")
print("Type 'exit' to quit.\n")

while True:
    user_query = input("You: ").strip()

    if user_query.lower() in ["exit", "quit", "bye"]:
        print("\nAssistant: Goodbye!")
        break

    response = bot.generate(user_query)
    print(f"Assistant: {response}\n")
