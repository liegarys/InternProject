import wave
import numpy as np
import matplotlib.pyplot as plt

# Define the function to calculate decibels
def calculate_decibels(data):
    """Calculate the RMS value of the audio signal and convert it to dB."""
    rms = np.sqrt(np.mean(np.square(data)))
    if rms > 0:
        db = 20 * np.log10(rms)
    else:
        db = -np.inf  # Negative infinity if rms is zero (no sound)
    return db

# Function to read WAV file and process audio data
def process_wav_file_in_chunks(file_path, chunk_size, threshold):
    # Open the WAV file
    with wave.open(file_path, 'r') as wav_file:
        # Get audio parameters
        n_channels = wav_file.getnchannels()
        sampwidth = wav_file.getsampwidth()
        framerate = wav_file.getframerate()
        n_frames = wav_file.getnframes()


        num_chunks = 0  # Initialize chunk counter
        decibel_levels = []  # List to store decibel levels for visualization
        time_points = []  # List to store time points for each chunk
        
        print(f"Channels: {n_channels}, Sample width: {sampwidth}, Frame rate: {framerate}, Number of frames: {n_frames}")
      
        # Read and process the audio data in chunks
        for i in range(0, n_frames, chunk_size):
            # Read a chunk of audio data
            num_chunks += 1  # Increment chunk counter


            audio_data = wav_file.readframes(chunk_size)
            
            # Convert audio data to numpy array
            if sampwidth == 1:  # 8-bit audio
                data = np.frombuffer(audio_data, dtype=np.uint8)
                data = data - 128  # Convert unsigned to signed
            elif sampwidth == 2:  # 16-bit audio
                data = np.frombuffer(audio_data, dtype=np.int16)
            elif sampwidth == 4:  # 32-bit audio
                data = np.frombuffer(audio_data, dtype=np.int32)
            else:
                raise ValueError(f"Unsupported sample width: {sampwidth}")
            
            # If stereo, select only one channel (e.g., left channel)
            if n_channels > 1:
                data = data[::n_channels]
            
            if np.all(data == 0):
                db = -np.inf  # Assign -inf dB for silent chunks
            else:
                # Calculate the decibel level
                db = calculate_decibels(data)

            # Append decibel level and time point for visualization
            decibel_levels.append(db)
            time_points.append(i / framerate)

        '''
            # Check if the dB level exceeds the threshold
            if db > threshold:
                print(f"Sound detected in chunk {i // chunk_size + 1}: {db:.2f} dB")
                # Add your processing code here
            else:
                print(f"Below threshold in chunk {i // chunk_size + 1}: {db:.2f} dB")

        '''
                    # Calculate the duration of the audio file
        total_frames = num_chunks * chunk_size
        duration_seconds = total_frames / framerate

        print(f"Total chunks: {num_chunks}")
        print(f"Duration: {duration_seconds:.2f} seconds")

        # Visualize the audio waveform and decibel levels
        plt.figure(figsize=(10, 8))

        # Plot the audio waveform
        # Plot the audio waveform
        wav_file.rewind()
        audio_data = np.frombuffer(wav_file.readframes(n_frames), dtype=np.int16)
        time_array = np.linspace(0, n_frames / framerate, num=n_frames)
        plt.plot(time_array, audio_data, label='Audio Waveform')

        # Detect threshold crossings
        threshold_value = 200
        crossings = np.where((audio_data[:-1] < threshold_value) & (audio_data[1:] >= threshold_value) | 
                             (audio_data[:-1] >= threshold_value) & (audio_data[1:] < threshold_value))[0]
        crossing_times = time_array[crossings]
        crossing_values = audio_data[crossings]
        plt.plot(crossing_times, crossing_values, 'ro', label='Threshold Crossings')


        # Clip audio where it satisfies the threshold_value condition
        start_index = crossings[0]
        end_index = crossings[-1]
        clipped_audio_data = audio_data[start_index:end_index]

        # Save clipped audio to a new WAV file
        output_file_path = "clipped_audio.wav"
        with wave.open(output_file_path, 'w') as output_wav_file:
            output_wav_file.setnchannels(n_channels)
            output_wav_file.setsampwidth(sampwidth)
            output_wav_file.setframerate(framerate)
            output_wav_file.writeframes(clipped_audio_data.tobytes())

        print(f"Cropped Time: {crossing_times[-1] - crossing_times[0] : .2f}")
        print(f"Clipped audio saved to {output_file_path}")

        plt.show()


# Example usage
file_path = "D:\\Python Course\\ses_kayitlari\\OurRecordings\\deneme.wav"

chunk_size = 1024  # Number of frames per chunk
threshold = 30  # dB threshold

process_wav_file_in_chunks(file_path, chunk_size, threshold)