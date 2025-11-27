import asyncio
import aiohttp
from livekit.agents import AutoSubscribeAgent, InputAudioStream, OutputAudioStream

FASTAPI_URL = "http://localhost:8000/chat"

async def call_langchain_api(text):
    async with aiohttp.ClientSession() as session:
        async with session.post(FASTAPI_URL, json={"user_query": text}) as resp:
            data = await resp.json()
            return data["response"]


class LegalAidVoiceAgent(AutoSubscribeAgent):

    async def on_audio_stream(self, audio: InputAudioStream):
        async for transcript in audio.transcriptions():
            user_msg = transcript.text
            print("User:", user_msg)

            # Send to LangChain backend
            reply = await call_langchain_api(user_msg)
            print("Bot:", reply)

            # TTS out
            out = OutputAudioStream()
            await out.tts(reply, voice="female")

            self.room.publish_track(out, name="assistant_voice")
