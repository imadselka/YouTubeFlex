from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import re
import yt_dlp
import shutil
import time
import json
from typing import Generator
from urllib.parse import unquote

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FFMPEG_LOCATION = os.path.join(os.getcwd(), "ffmpeg", "ffmpeg.exe" if os.name == "nt" else "ffmpeg")
TEMP_DOWNLOADS_FOLDER = "temp_downloads"

def is_valid_youtube_url(url: str) -> bool:
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    return bool(re.match(youtube_regex, url))

def ffmpeg_available():
    return shutil.which(FFMPEG_LOCATION) is not None or os.path.exists(FFMPEG_LOCATION)

def stream_with_context(generator: Generator) -> StreamingResponse:
    return StreamingResponse(generator, media_type="text/event-stream")

async def process_download(url: str, format: str):
    if not is_valid_youtube_url(url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    start_time = time.time()
    download_start = 0
    conversion_start = 0
    file_path = ""

    def ydl_hook(d):
        nonlocal download_start, conversion_start, file_path
        if d['status'] == 'downloading':
            if download_start == 0:
                download_start = time.time()
            progress = float(d['downloaded_bytes'] / d['total_bytes']) * 100 if d['total_bytes'] else 0
            elapsed = time.time() - download_start
            estimated_total = elapsed / (progress / 100) if progress > 0 else 0
            remaining = estimated_total - elapsed
            yield f"data: {json.dumps({'type': 'download', 'progress': progress, 'eta': remaining})}\n\n"
        elif d['status'] == 'finished':
            file_path = d['filename']
            conversion_start = time.time()
            yield f"data: {json.dumps({'type': 'download', 'progress': 100, 'eta': 0})}\n\n"

    ydl_opts = {
        'format': 'bestaudio/best' if format == 'mp3' else 'bestvideo+bestaudio/best',
        'outtmpl': f'{TEMP_DOWNLOADS_FOLDER}/%(title)s.%(ext)s',
        'progress_hooks': [ydl_hook],
    }

    if ffmpeg_available():
        ydl_opts['ffmpeg_location'] = FFMPEG_LOCATION
        if format == 'mp3':
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            if format == 'mp3':
                file_path = file_path.rsplit('.', 1)[0] + '.mp3'
            else:
                file_path = file_path.rsplit('.', 1)[0] + '.mp4'

        # Simulate conversion progress
        for i in range(101):
            progress = i
            elapsed = time.time() - conversion_start
            estimated_total = elapsed / (progress / 100) if progress > 0 else 0
            remaining = estimated_total - elapsed
            yield f"data: {json.dumps({'type': 'conversion', 'progress': progress, 'eta': remaining})}\n\n"
            time.sleep(0.05)  # Adjust this value to control the speed of the simulated progress

        yield f"data: {json.dumps({'type': 'complete', 'file_path': os.path.basename(file_path)})}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

@app.post("/download")
async def download_video_post(url: str = Form(...), format: str = Form(...)):
    return stream_with_context(process_download(url, format))

@app.get("/get-file/{file_name}")
async def get_file(file_name: str):
    file_name = unquote(file_name)
    file_path = os.path.join(TEMP_DOWNLOADS_FOLDER, file_name)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=file_name, media_type='application/octet-stream')
    else:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

@app.on_event("startup")
async def startup_event():
    os.makedirs(TEMP_DOWNLOADS_FOLDER, exist_ok=True)

@app.on_event("shutdown")
async def shutdown_event():
    shutil.rmtree(TEMP_DOWNLOADS_FOLDER, ignore_errors=True)