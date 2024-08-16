# InternProject

## This project is a voice recognition project using embedded device and deep learning algorithms


### Features

##### In this repository, there are folders that work interdependently and folders that work independently of each other:

- **"Interface" folder** is very important folder for this project, it includes python interface where we can record voice, open voice and crop voice according to some threshold value then send this audio to "model" folder to implement voice recognition model ("Interface" and  "model" folders work dependently of each other)

- **'Model' folder** contains our edge-impulse deep learning model and the necessary libraries.

- **"captureAudio_filterli_calisir_filteryi_iyi_calistiriyor" folder** allows us to capture audio for EspEye and apply a Butterworth Filter to the captured audio. The low-pass filter effectively reduces high-frequency noise, ensuring that only the desired lower frequencies pass through, which improves the overall audio quality.

- **'YoutubeAudioClipping' folder** contains a Python file where you can provide Turkish keywords that you want to capture and a YouTube URL for searching. The script will then generate clipped audio files for your keywords.
Note: The Python file searches for keywords in subtitles, so choose videos that already have subtitles or ones where subtitles can be generated automatically.

- **'AudiodBThreshold' folder** contains my work for testing my code file by file. I ran the code in pieces, then modified and merged them. (You likely won't need this folder much.)



## Installation

**Note :** The “captureAudio_filterli_calisir_filteryi_iyi_calistiriyor" folder contains the files you need to receive the audio via esp, and the **“model”** and **“interface”** folders are the folders you need to run the voice recognition model

If you plan to download and run this project directly, the two folders that will be most useful are the 'Interface' and 'model' folders, but you will need to reorganize the file paths so that these files can work with each other and to get the sounds from one place and save them correctly.

#### When you clone this project, some modifications are required due to file paths:
- **In Interface (interface.py):**
In the record_audio function, you need to modify *directory = "//..."* to your actual path for saving your recordings.

- In the **process_wav_file_in_chunks** function, you need to modify *input_file_path = f"...//{file_name}.wav*" depending on whether you are processing an existing WAV file from one of your folders or applying this process to an audio file recorded using the interface

- In the **send_audio function**, you need to modify *working_dir = ".../model"* to the correct path to access the 'Model' folder, where the voice recognition model files and folders are stored.

**Note: Also, since this repository already contains an executable file, I put the part we compile in the comment line. If you want to compile it yourself, you can remove this part from the comment line.**


