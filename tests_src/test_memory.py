import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT)

from src.memory_chain import MemoryChatbot

bot = MemoryChatbot()

print(bot.ask("My name is Ramesh."))
print(bot.ask("I live in Mysuru."))
print(bot.ask("Who am I?"))
print(bot.ask("Where do I live?"))
print(bot.ask("I am a daily wage worker."))
print(bot.ask("What do I do for a living?"))

