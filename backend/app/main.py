from fastapi import FastAPI, Form, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import re
import yt_dlp
import shutil

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust the allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to the bundled ffmpeg binary (for both Windows and Linux/macOS)
FFMPEG_LOCATION = os.path.join(os.getcwd(), "ffmpeg", "ffmpeg.exe" if os.name == "nt" else "ffmpeg")

# Helper function to validate YouTube URL
def is_valid_youtube_url(url: str) -> bool:
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    return bool(re.match(youtube_regex, url))

# Check if ffmpeg is available locally
def ffmpeg_available():
    return shutil.which(FFMPEG_LOCATION) is not None or os.path.exists(FFMPEG_LOCATION)

# Process the YouTube download
async def process_download(url: str, format: str):
    if not is_valid_youtube_url(url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
    try:
        # Set yt-dlp options based on the format (mp3 or mp4)
        ydl_opts = {
            'format': 'bestaudio/best' if format == 'mp3' else 'bestvideo+bestaudio/best',
            'outtmpl': 'temp_downloads/%(title)s.%(ext)s',  # Save file using YouTube title
        }

        # Add ffmpeg location to the options if available
        if ffmpeg_available():
            ydl_opts['ffmpeg_location'] = FFMPEG_LOCATION

            # If downloading mp3, we need ffmpeg for postprocessing
            if format == 'mp3':
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',  # Convert video to mp4
                }]

        # Download and process the video/audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

            # Adjust the file path for mp3
            if format == 'mp3':
                file_path = file_path.rsplit('.', 1)[0] + '.mp3'
            else:
                file_path = file_path.rsplit('.', 1)[0] + '.mp4'

        # Serve the file for download
        return FileResponse(file_path, filename=os.path.basename(file_path))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# POST route to download the video
@app.post("/download")
async def download_video_post(url: str = Form(...), format: str = Form(...)):
    return await process_download(url, format)

# GET route to download the video (in case you need it)
@app.get("/download")
async def download_video_get(url: str = Query(...), format: str = Query(...)):
    return await process_download(url, format)

# Create the downloads folder on startup
@app.on_event("startup")
async def startup_event():
    os.makedirs("temp_downloads", exist_ok=True)

# Cleanup the downloads folder on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    shutil.rmtree("temp_downloads", ignore_errors=True)
