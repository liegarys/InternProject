import tkinter as tk
import matplotlib.pyplot as plt
from tkinter import ttk

import pyaudio
import wave
import time
import numpy as np
import subprocess

import os 




# Constants
FRAMES_PER_BUFFER = 1024 #Chunk size
FORMAT = pyaudio.paInt16 # Format of the audio samples (16-bit)
CHANNELS = 1  #  # Number of audio channels (1 for MONO)
RATE = 16000 #sample rate
SLEEP_TIME = 0.005  # 5 milliseconds
BUFFER_FRAMES = 10  # Number of initial frames to buffer and discard



th = 200


def check_entry_content(*args):
    if file_name_entry.get():  # If there's text in the entry
        record_button.config(state=tk.DISABLED)  # Disable the record button
    else:
        record_button.config(state=tk.NORMAL)  # Enable the record button if the entry is empty






def get_next_file_number(directory, prefix):
    files = os.listdir(directory)
    max_num = 0
    for file in files:
        if file.startswith(prefix) and file.endswith(".wav"):
            try:
                num = int(file[len(prefix):-4])
                if num > max_num:
                    max_num = num
            except ValueError:
                continue
    return max_num + 1


def clear_prediction_label():
    predictedKeyword_label.config(text="")


def parse_predictions(result_string):
    # Find the "Predictions:" line and extract the following lines
    predictions_section = result_string.split("Predictions:")[1].strip()
    
    # Extract the predictions from the result string
    predictions = {}
    lines = predictions_section.split("\n")
    
    for line in lines:
        if ": " in line:
            keyword, value = line.split(": ")
            predictions[keyword.strip()] = float(value.strip())

    return predictions



def record_audio():

    global current_file_name

    directory = "//home//ali//Desktop//our_recordings"
    prefix = "audio_"

    clear_prediction_label()

    file_number = get_next_file_number(directory, prefix)
    current_file_name = f"{prefix}{file_number}"
    
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
            status_label.config(text=f"Time Left: {seconds - elapsed_seconds} seconds")
            root.update_idletasks()  # Update the Tkinter interface

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
    print(type(normalized_audio_data))
    print("Lenght: ", len(normalized_audio_data))

    # Save the normalized audio to a new WAV file
    #filename = "deneme"
    output_file_path = os.path.join(directory, f"{current_file_name}.wav")

    with wave.open(output_file_path, 'w') as output_wav_file:
        output_wav_file.setnchannels(CHANNELS)
        output_wav_file.setsampwidth(pa.get_sample_size(FORMAT))
        output_wav_file.setframerate(RATE)
        output_wav_file.writeframes(normalized_audio_data.tobytes())

    
    return current_file_name


# Function to read WAV file and process audio data
def process_wav_file_in_chunks(file_name, chunk_size, threshold):
    global clipped_audio_data

    clear_prediction_label()


    if(file_name_entry.get()):
        input_file_path = f"//home//ali//Desktop//wavFiles//{file_name}.wav"

    else:
        input_file_path = f"//home//ali//Desktop//our_recordings//{file_name}.wav"
   
    
    output_file_path = f"//home//ali//Desktop//our_recordings//{file_name}.wav"

    try:
        # Open the WAV file
        with wave.open(input_file_path, 'r') as wav_file:
            # Get audio parameters
            n_channels = wav_file.getnchannels()
            sampwidth = wav_file.getsampwidth()
            framerate = wav_file.getframerate()
            n_frames = wav_file.getnframes()


            num_chunks = 0  # Initialize chunk counter
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


            # Calculate the duration of the audio file
            total_frames = num_chunks * chunk_size
            duration_seconds = total_frames / framerate

            print(f"Total chunks: {num_chunks}")
            print(f"Duration: {duration_seconds:.2f} seconds")


            # Close any previous figures to ensure only one figure is open
            plt.close('all')

            # Visualize the audio waveform and decibel levels
            plt.figure(figsize=(10, 8))

            # Plot the audio waveform
            wav_file.rewind()
            audio_data = np.frombuffer(wav_file.readframes(n_frames), dtype=np.int16)
            time_array = np.linspace(0, n_frames / framerate, num=n_frames)
            plt.plot(time_array, audio_data, label='Audio Waveform')

            # Detect threshold crossings
            threshold_value = threshold
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
            #output_file_path = "clipped_audio.wav"
            with wave.open(output_file_path, 'w') as output_wav_file:
                output_wav_file.setnchannels(n_channels)
                output_wav_file.setsampwidth(sampwidth)
                output_wav_file.setframerate(framerate)
                output_wav_file.writeframes(clipped_audio_data.tobytes())

            print(f"Cropped Time: {crossing_times[-1] - crossing_times[0] : .2f}")
            print(f"Clipped audio saved to {output_file_path}")


            # If clipped audio data is larger than expected, handle the error
            if len(clipped_audio_data) > 16000:
                return 1  # Return error code

            plt.show()

    except FileNotFoundError as e:
        # Update status_label with the error message
        return 1

    except Exception as e:
        # Catch any other exceptions and display the error message
        status_label.config(text=f"Error: {str(e)}")
        return 1
    

    return 0


# Tkinter Interface
def start_recording():
    #file_name = file_name_entry.get()
    current_file_name = record_audio()
    status_label.config(text=f"Recorded and saved as {current_file_name}.wav")



def start_cropping():
    global current_file_name

    if(file_name_entry.get()):
        current_file_name = file_name_entry.get()

    result = process_wav_file_in_chunks(current_file_name, FRAMES_PER_BUFFER, threshold= th)  # Example chunk size and threshold
    
    if result == 0 :
        status_label.config(text=f"Cropped and saved as cropped_{current_file_name}.wav")
        send_button.config(state=tk.NORMAL)  # Enable the "Send Audio" button if processing succeeded

    
    if result == 1 :
        status_label.config(text="File not found\nOr audio data is larger than expected (16000 samples).")
        send_button.config(state=tk.DISABLED)  # Disable the "Send Audio" button if processing failed



def send_audio():
    global current_file_name
    global clipped_audio_data
    try:
        # Define the directory and the command
        working_dir = '//home//ali//Desktop/example-standalone-inferencing'  # Replace with the actual path
        command = './build/app'

        print("Type: " , type(clipped_audio_data))
        print("Length : ", len(clipped_audio_data))


        # Ensure clipped_audio_data is padded to the desired length
        desired_length = 16000
        if len(clipped_audio_data) < desired_length:
            padding_length = desired_length - len(clipped_audio_data)
            clipped_audio_data = np.pad(clipped_audio_data, (0, padding_length), 'constant')

        print("Type: ", type(clipped_audio_data))
        print("Length: ", len(clipped_audio_data))

        # Save clipped_audio_data to a file
        features_file_path = f"//home//ali//Desktop//our_recordings//{current_file_name}_features.txt"
        np.savetxt(features_file_path, [clipped_audio_data], delimiter=',', fmt='%f')

        
        # Check if the executable exists in the specified directory
        app_path = os.path.join(working_dir, command)
        if not os.path.isfile(app_path):
            output_text.delete('1.0', tk.END)
            output_text.insert(tk.END, f"Error: Executable not found at {app_path}")
            return
        
        '''
        COMPILE

        # Compile the C++ code
        print("COMPILE")
        compile_command = 'make -j4'
        compile_result = subprocess.run(compile_command, cwd=working_dir, shell=True)
        
        # Check for compilation errors
        if compile_result.returncode != 0:
            output_text.delete('1.0', tk.END)
            output_text.insert(tk.END, "Compilation failed.")
            print("Compilation stderr:", compile_result.stderr)
            return
        
        
        '''    

        # Full path to the .wav file to be sent
        wav_file_path = f"//home//ali//Desktop//our_recordings//{current_file_name}.wav"
        
        # Run the command in the specified directory and pass the .wav file path as an argument
        print("RUN")
        # Run the command in the specified directory and pass the features file path as an argument
        #With capture_output = True we can capture the standard output and standard error from our C++ program
        result = subprocess.run([command, features_file_path], cwd=working_dir, capture_output=True, text=True)

        # Parse the predictions from the result.stdout
        predictions = parse_predictions(result.stdout)

        # Find the keyword with the highest prediction value
        if predictions:
            highest_keyword = max(predictions, key=predictions.get)
            highest_value = predictions[highest_keyword]

            # Update the status label to show the highest prediction
            predictedKeyword_label.config(text=f"Prediction: '{highest_keyword}' with a value of {highest_value:.2f}")
        
        # Display the output in the text box
        print("Return code:", result.returncode)
        print("stdout:", result.stdout)
        print("stderr:", result.stderr)



        # Display the output in the text box
        output_text.delete('1.0', tk.END)
        output_text.insert(tk.END, result.stdout)

    
    
    except Exception as e:
        output_text.delete('1.0', tk.END)
        output_text.insert(tk.END, f"Error: {str(e)}")






# Initialize the Tkinter window
root = tk.Tk()
root.title("Audio Recorder")
root.geometry("600x600")

top_frame = tk.Frame(root)
top_frame.pack(pady=20)

top2_frame = tk.Frame(root)
top2_frame.pack(pady=20)

middle_frame = tk.Frame(root)
middle_frame.pack(pady=10)


bottom_frame = tk.Frame(root)
bottom_frame.pack(pady=20)

# Create and place widgets
file_name_label = tk.Label(top_frame, text="Leave empty to record a new audio, or enter a name to process an existing file:")
file_name_label.pack(side=tk.LEFT, padx=5)

file_name_entry = tk.Entry(top2_frame)
file_name_entry.pack(padx=5, anchor= tk.CENTER)

predictedKeyword_label = tk.Label(master= top2_frame, anchor= tk.CENTER)
predictedKeyword_label.pack(pady=5)

# Binding to enable or disable the "Record Audio" button based on whether a file name is entered
file_name_entry.bind("<KeyRelease>", check_entry_content)


'''
deneme_label = tk.Label(master= root)
deneme_label.config(text= "naber")
deneme_label.pack()

deneme_entry = tk.Entry(master= root)
deneme_entry.pack()

deneme_button = tk.Button(master = root)
deneme_button.config(text="Gaza Bas", command= print)
deneme_button.pack()

'''
record_button = tk.Button(middle_frame, text="Record Audio", command=start_recording)
record_button.pack(side=tk.LEFT, padx=10, pady=10)

crop_button = tk.Button(middle_frame, text="Open/Crop Audio", command=start_cropping)
crop_button.pack(side=tk.LEFT, padx=10, pady=10)

send_button = tk.Button(middle_frame, text="Send Audio", command=send_audio)
send_button.pack(side=tk.LEFT, padx=10, pady=10)

# Create a text box to display the output
output_text = tk.Text(bottom_frame, height=10, width=60)
output_text.pack(pady=10)

status_label = tk.Label(bottom_frame, text="")
status_label.pack(pady=20)  # Add vertical padding


custom_font = ("Helvetica", 12, "bold")

file_name_label.config(font=custom_font)
file_name_entry.config(font=custom_font)
predictedKeyword_label.config(font=custom_font)
record_button.config(font=custom_font)
crop_button.config(font=custom_font)
send_button.config(font=custom_font)
output_text.config(font=custom_font)
status_label.config(font=custom_font)




#Color
root.config(bg="darkblue")
top_frame.config(bg= "darkblue")
top2_frame.config(bg="darkblue")
middle_frame.config(bg="darkblue")
bottom_frame.config(bg="darkblue")

file_name_label.config(bg="darkblue", fg="white")
status_label.config(bg="darkblue", fg="white")
predictedKeyword_label.config(bg="darkblue", fg="yellow")
record_button.config(bg="black", fg="white")
crop_button.config(bg="black", fg="white")
send_button.config(bg="black", fg="white")




# Start the Tkinter event loop
root.mainloop()