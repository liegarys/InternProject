import pyaudio
import numpy as np

# Audio settings
CHUNK = 1024   #Chunk sayisini dusurerek  latency i azaltabiliriz mesela 256 veya 512 e alarak
FORMAT = pyaudio.paInt16  
CHANNELS = 1  #MONO Stero falan
RATE = 16000  

# dB threshold 
THRESHOLD = 25  # Adjust this value as needed

def calculate_decibels(data):
    """Calculate the RMS value of the audio signal and convert it to dB."""
    rms = np.sqrt(np.mean(np.square(data)))
    if rms > 0:
        db = 20 * np.log10(rms)
    else:
        db = -np.inf  # Negative infinity if rms is zero (no sound)
    return db

def main():
    # Initialize PyAudio
    audio = pyaudio.PyAudio()


    # Open audio stream
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

    print("Listening for sound...")

    try:
        while True:
            # Read audio data from the stream
            data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)

            # Calculate the dB level of the audio
            db = calculate_decibels(data)

            # Check if the dB level exceeds the threshold
            if db > THRESHOLD:
                print(f"Sound detected: {db:.2f} dB")
                # Add your processing code here
            else:
                print(f"Below threshold: {db:.2f} dB")
    
    except KeyboardInterrupt:
        print("Stopped listening.")

    finally:
        # Clean up the audio stream
        stream.stop_stream()
        stream.close()
        audio.terminate()

if __name__ == "__main__":
    main()
