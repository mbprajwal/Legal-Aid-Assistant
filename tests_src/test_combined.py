import sys
sys.path.append(".")

from src.combined_chain import CombinedLegalChatbot

bot = CombinedLegalChatbot()

questions = [
    "My name is Ramesh",
    "I live in Mysuru",
    "Who am I?",
    "I am a daily wage worker",
    "What do I do for a living?",
    "I have a dispute regarding tenancy rights.",
    "I want to know the difference between a plaint and a petition.",
    "I need help with a boundary encroachment dispute.",
]

for q in questions:
    print("\nUSER:", q)
    print("ASSISTANT:", bot.generate(q))
