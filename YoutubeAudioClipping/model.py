
from moviepy.video.io.VideoFileClip import VideoFileClip
import pysrt
import os
import time

from pytubefix import YouTube
from pytubefix.cli import on_progress


def download_youtube_video(url, path = "video.mp4"):

    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        print(yt.title)

        ys = yt.streams.get_highest_resolution()
        ys.download(output_path= path)
        return  [yt.title ,path]

    except:
        print("Hata indirmede")

def download_subtitles(url, output_path='subtitles.srt'):
    yt = YouTube(url)
    caption = yt.captions.get_by_language_code('tr')
    if not caption:
        caption = yt.captions.get_by_language_code('a.tr')
    if caption:
        caption_srt = caption.generate_srt_captions()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(caption_srt)
        return output_path
    else:
        raise ValueError("No Turkish subtitles found for this video, either manually added or auto-generated.")

def parse_subtitles(subtitles_path):
    return pysrt.open(subtitles_path)

def clip_audio(video_path, subtitles, keywords, output_folder='audio_clips'):
    os.makedirs(output_folder, exist_ok=True)
    if not os.path.exists(video_path):
        print(f"Error: The video file {video_path} does not exist.")
        return
    
    try:
        video = VideoFileClip(video_path)
        video_duration = video.duration  # Attempt to read the video duration
        print(f"Video duration: {video_duration} seconds")
    except Exception as e:
        print(f"Error loading video file: {e}")
        return

    for keyword in keywords:
        for subtitle in subtitles:
            if keyword.lower() in subtitle.text.lower():
                start_time = max(0, subtitle.start.ordinal / 1000 - 1)
                end_time = min(video.duration, start_time + 5)
                audio_clip = video.audio.subclip(start_time, end_time)
                audio_path = os.path.join(output_folder, f'{keyword}_{subtitle.index}.mp3')
                try:
                    audio_clip.write_audiofile(audio_path)
                    print(f'Audio clip saved: {audio_path}')
                except Exception as e:
                    print(f"Error saving audio clip: {e}")

    video.close()  # Ensure the video file is closed




youtube_url = 'https://www.youtube.com/watch?v=s9RWGA2X9FM'
#path = "C:\\Users\\lenovo\\OneDrive\\Masaüstü\\Ogrenimler\\twitter video"

keywords = ['evet', 'tamam', 'yaralandım']  # Add your keywords here
[title, path] = download_youtube_video(url=youtube_url)


#video_path = title.replace('"', '')
title = "Fatih Altaylı yorumluyor Şerefsizliğin sonu sınırı yok!"
video_path = f"{path}/{title}.mp4"
print(video_path)

if video_path:
    # Adding a delay to ensure the file system has completed the write operations
    time.sleep(2)
    try:
        subtitles_path = download_subtitles(youtube_url)
        subtitles = parse_subtitles(subtitles_path)
        clip_audio(video_path, subtitles, keywords)
    except Exception as e:
        print(f"Error processing subtitles or clipping audio: {e}")
