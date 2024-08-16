import pyaudio
import wave
import time
import numpy as np

# Constants
FRAMES_PER_BUFFER = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1  # MONO
RATE = 16000


BUFFER_FRAMES = 10  # Number of initial frames to buffer and discard

# Initialize PyAudio
pa = pyaudio.PyAudio()

# Open the stream
stream = pa.open(
    rate=RATE,
    format=FORMAT,
    channels=CHANNELS,
    frames_per_buffer=FRAMES_PER_BUFFER,
    input=True
)

print("Start Recording")

seconds = 5
frames = []
buffered_frames = []

# Record audio with initial buffering
for i in range(0, int(RATE / FRAMES_PER_BUFFER * seconds) + BUFFER_FRAMES):
    data = stream.read(FRAMES_PER_BUFFER)

    # Buffer the initial frames to discard initial impulse noise
    if i < BUFFER_FRAMES:
        buffered_frames.append(data)
        continue

    # Append data after the buffer period
    frames.append(data)
    

    # Print recording progress
    if (i - BUFFER_FRAMES) % int(RATE / FRAMES_PER_BUFFER) == 0 and i >= BUFFER_FRAMES:
        elapsed_seconds = (i - BUFFER_FRAMES) // int(RATE / FRAMES_PER_BUFFER)
        print(f"Time Left: {seconds - elapsed_seconds}")

print("Recording Stopped")

# Stop and close the stream
stream.stop_stream()
stream.close()
pa.terminate()

# Convert the list of frames to a numpy array for normalization
audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)

''''
# Normalize the audio data to increase the amplitude
max_val = np.max(np.abs(audio_data))
normalized_audio_data = (audio_data / max_val) * (2**15 - 1)
normalized_audio_data = normalized_audio_data.astype(np.int16)
'''

normalized_audio_data = audio_data

# Save the normalized audio to a new WAV file
filename = "deneme"
output_file_path = f"D:\\Python Course\\ses_kayitlari\\OurRecordings\\{filename}.wav"

with wave.open(output_file_path, 'w') as output_wav_file:
    output_wav_file.setnchannels(CHANNELS)
    output_wav_file.setsampwidth(pa.get_sample_size(FORMAT))
    output_wav_file.setframerate(RATE)
    output_wav_file.writeframes(normalized_audio_data.tobytes())
