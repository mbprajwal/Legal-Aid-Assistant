# # agent_worker.py

# # 1. IMPORTS
# import os
# from livekit.agents import AgentSession, Agent, cli, JobContext, WorkerOptions
# from livekit.plugins import langchain, openai
# from livekit.plugins.vad.signal_processing import FftVAD
# from langchain_core.runnables import RunnableLambda
# from dotenv import load_dotenv

# # Import your custom class from the src folder
# from src.combined_chain import CombinedLegalChatbot

# load_dotenv() # Load LIVEKIT/OPENAI keys from .env
# # Use the string name of the environment variable as the argument to os.getenv()
# LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
# LIVEKIT_API_SECRET= os.getenv("LIVEKIT_API_SECRET")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# # 2. INSTANTIATE AND WRAP YOUR CORE LOGIC (at the top level)
# # This creates a single instance of your stateful chatbot logic
# core_chatbot_instance = CombinedLegalChatbot(model_name=os.getenv("LLAMA_MODEL", "llama2"))

# # Wrap the .generate() method into a LangChain Runnable
# rag_brain_runnable = RunnableLambda(
#     lambda query, **kwargs: core_chatbot_instance.generate(query)
# ).with_types(
#     input_type=str,
#     output_type=str
# )


# # 3. LIVEKIT ENTRYPOINT FUNCTION
# async def entrypoint(ctx: JobContext):
#     await ctx.connect()
    
#     # Configure the Agent Session using your wrapped logic
#     session = AgentSession(
#         llm=langchain.LLMAdapter(rag_brain_runnable),
#         vad=FftVAD(),
#         stt=openai.STT(), # Requires OPENAI_API_KEY
#         tts=openai.TTS(), # Requires OPENAI_API_KEY
#     )

#     agent = Agent(
#         instructions="You are a legal aid assistant. Be concise and helpful.",
#     )

#     print(f"Agent connected to room: {ctx.room.name}. Session starting...")
#     await session.start(agent=agent, room=ctx.room)
    

# # 4. RUNNER
# if __name__ == "__main__":
#     cli.run_app(
#         WorkerOptions(
#             entrypoint_fnc=entrypoint
#         )
#     )

# agent_worker.py
# agent_worker.py

# voice_chat.py

# voice_chat.py

# voice_chat.py

import os
import asyncio
from dotenv import load_dotenv

from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins.langchain import LLMAdapter
from livekit.plugins.silero import VAD
from livekit.plugins.openai import STT, TTS

from langchain_core.runnables import RunnableLambda

# Your custom LangChain RAG brain
from src.combined_chain import CombinedLegalChatbot

# -----------------------------------------------------------
# Load environment variables
# -----------------------------------------------------------
load_dotenv()

LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
    raise ValueError("❌ LIVEKIT keys missing in .env")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY missing in .env")


# -----------------------------------------------------------
# Initialize your RAG chatbot instance ONCE
# -----------------------------------------------------------
print("🧠 Loading RAG-based CombinedLegalChatbot…")
rag_bot = CombinedLegalChatbot(
    model_name=os.getenv("LLAMA_MODEL", "llama2")
)

rag_runnable = RunnableLambda(
    lambda query, **kwargs: rag_bot.generate(query)
).with_types(input_type=str, output_type=str)


# -----------------------------------------------------------
# LiveKit Agent Entrypoint
# -----------------------------------------------------------
async def entrypoint(ctx: JobContext):
    print("🔌 Connecting agent to LiveKit room…")
    await ctx.connect()

    print(f"📡 Connected to room: {ctx.room.name}")

    # Step 1: Create Agent Session (without VAD first)
    session = AgentSession(
        llm=LLMAdapter(rag_runnable),
        stt=STT(api_key=OPENAI_API_KEY),
        tts=TTS(api_key=OPENAI_API_KEY),
    )

    # Step 2: Create VAD with correct API for your version
    print("🔊 Initializing Silero VAD…")
    vad = VAD(
        session=session,
        opts=VAD.Options(
            threshold=0.5,
            min_voiced_duration=0.2,
            min_silence_duration=0.25,
        )
    )
    session.vad = vad  # Attach VAD to session

    print("✅ Silero VAD initialized!")

    # Step 3: Create agent behavior
    agent = Agent(
        instructions=(
            "You are a legal aid assistant for Indian citizens. "
            "Be concise, factual, and avoid hallucinations. "
            "Use simple language so even non-experts can understand."
        )
    )

    # Step 4: Start real-time session
    print("🚀 Starting LiveKit voice session…")
    await session.start(agent=agent, room=ctx.room)


# -----------------------------------------------------------
# Worker runner
# -----------------------------------------------------------
if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            api_key=LIVEKIT_API_KEY,
            api_secret=LIVEKIT_API_SECRET,
        )
    )


