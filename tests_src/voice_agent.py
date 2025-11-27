from livekit.agents import AutoAgent, cli
from livekit.agents.llm import LLM
from livekit.agents.stt import WhisperSTT
from livekit.agents.tts import OpenAI_TTS

class LegalAidAgent(AutoAgent):
    def __init__(self):
        super().__init__(
            stt=WhisperSTT(model="base"),
            llm=LLM(
                model="llama3",
                system_prompt="You are an Indian legal assistant..."
            ),
            tts=OpenAI_TTS(voice="alloy"),
        )

if __name__ == "__main__":
    cli.run_app(LegalAidAgent())
