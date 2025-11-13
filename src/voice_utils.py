# src/voice_utils.py

import sounddevice as sd
import numpy as np
import tempfile
from scipy.io.wavfile import write as write_wav
import whisper
import os

# -----------------------------
# Record audio until Enter
# -----------------------------
def record_audio(sample_rate=16000):
    print("\n🎙 Recording... press ENTER to stop.\n")

    frames = []
    recording = True

    def callback(indata, frames_count, time_info, status):
        frames.append(indata.copy())

    # stop on Enter
    import threading
    def stop_on_enter():
        input()
        nonlocal recording
        recording = False

    threading.Thread(target=stop_on_enter, daemon=True).start()

    with sd.InputStream(samplerate=sample_rate, channels=1, callback=callback):
        while recording:
            sd.sleep(100)

    audio = np.concatenate(frames, axis=0)

    # save temp wav
    file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    write_wav(file.name, sample_rate, (audio * 32767).astype(np.int16))

    print(f"🎤 Saved recording: {file.name}\n")
    return file.name


# -----------------------------
# Whisper transcription
# -----------------------------
def transcribe(audio_path, model_size="base"):
    print("🔍 Transcribing...")

    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path, fp16=False)

    text = result.get("text", "").strip()

    # cleanup
    try: os.remove(audio_path)
    except: pass

    print(f"🗣️ You said: {text}\n")
    return text
