import pyaudio
import wave
import numpy as np

def detect_voice(stream):
    # Listen for voice activity
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        if np.abs(audio_data).mean() > THRESHOLD:
            return True

def record_audio(stream, output_file):
    frames = []
    print("Voice detected , starts recording...")
    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
            #sadaudio_data = np.frombuffer(data, dtype=np.int16)
            #if np.abs(audio_data).mean() < THRESHOLD:
            #    break
    except KeyboardInterrupt:
        pass  # Allows user to stop recording with CTRL+C or equivalent

    print("Saving recording...")

    with wave.open(output_file, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

if __name__ == "__main__":
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = 5
    THRESHOLD = 500  # Adjust this threshold according to your environment
    FILENAME = input("Enter the filename for saving the recording (without extension): ") + ".wav"

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("Listening for voice activity... Press CTRL+C to start recording immediately.")
    while True:
        try:
            if detect_voice(stream):
                record_audio(stream, FILENAME)
                break
        except KeyboardInterrupt:
            record_audio(stream, FILENAME)
            break

    stream.stop_stream()
    stream.close()
    audio.terminate()
    print("Recording saved to:", FILENAME)
