def record_audio(sample_rate=16000):
    import sounddevice as sd

    # List all devices
    devices = sd.query_devices()

    # Find first device with input channels
    input_device = None
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            input_device = i
            break

    if input_device is None:
        raise RuntimeError("\n❌ No input microphone detected on your system.\n"
                           "Go to Windows Sound Settings > Input > Choose a device.")

    print(f"\n🎙 Using microphone: {devices[input_device]['name']}\n")

    # Now start recording
    print("🎙 Recording... press ENTER to stop.\n")

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

    with sd.InputStream(
        samplerate=sample_rate,
        channels=1,
        device=input_device,   # 👉 FIXED (select specific input device)
        callback=callback
    ):
        while recording:
            sd.sleep(100)

    import numpy as np
    audio = np.concatenate(frames, axis=0)

    import tempfile
    from scipy.io.wavfile import write as write_wav

    file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    write_wav(file.name, sample_rate, (audio * 32767).astype(np.int16))

    print(f"\n🎤 Saved recording: {file.name}\n")
    return file.name
