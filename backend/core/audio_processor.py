from pydub import AudioSegment
import yt_dlp
import os
import sys

# =========================================================
# FFMPEG SETUP
# =========================================================

from dotenv import load_dotenv
import os

load_dotenv()


FFMPEG_PATH = os.getenv("FFMPEG_PATH")

if FFMPEG_PATH:
    os.environ["PATH"] += os.pathsep + FFMPEG_PATH

    AudioSegment.converter = os.path.join(
        FFMPEG_PATH,
        "ffmpeg.exe"
    )



# 2. DOWNLOAD FUNCTION
def download_youtube_audio(url: str) -> str:
    """Downloads audio from a YouTube URL and returns the local file path."""
    if not os.path.exists("downloades"):
        os.makedirs("downloades")
        
    output_path = os.path.join("downloades", "%(title)s.%(ext)s")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'ffmpeg_location': FFMPEG_PATH, 
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }
        ],
        'quiet': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
    
        base_path, _ = os.path.splitext(filename)
        actual_wav_path = base_path + ".wav"
        
        return actual_wav_path


# =========================================================
# CONVERT AUDIO
# =========================================================

def convert_to_wav(input_path: str) -> str:

    base_path, _ = os.path.splitext(input_path)

    output_path = base_path + "_converted.wav"

    audio = AudioSegment.from_file(input_path)

    audio = (
        audio
        .set_channels(1)
        .set_frame_rate(16000)
    )

    audio.export(
        output_path,
        format="wav"
    )

    return output_path

# =========================================================
# CHUNK AUDIO
# =========================================================

def chunk_audio(
    wav_path: str,
    chunk_seconds: int = 25
) -> list:

    audio = AudioSegment.from_wav(wav_path)

    chunk_ms = chunk_seconds * 1000

    chunks = []

    for i, start in enumerate(
        range(0, len(audio), chunk_ms)
    ):

        chunk = audio[start:start + chunk_ms]

        chunk_path = (
            f"{os.path.splitext(wav_path)[0]}"
            f"_chunk_{i}.wav"
        )

        chunk.export(
            chunk_path,
            format="wav"
        )

        chunks.append(chunk_path)

    return chunks

# =========================================================
# MAIN PROCESS FUNCTION
# =========================================================

def process_input(source: str) -> list:

    if (
        source.startswith("http://")
        or
        source.startswith("https://")
    ):

        print("Detected YouTube URL")
        print("Downloading audio...")

        wav_path = download_youtube_audio(source)

    else:

        print("Detected local file")
        print("Converting audio...")

        wav_path = convert_to_wav(source)

    print("Chunking audio...")

    chunks = chunk_audio(wav_path)

    print(f"{len(chunks)} chunk(s) created")

    return chunks