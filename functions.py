import os
from typing import Any
from yt_dlp import YoutubeDL

def download_media(url: str) -> None:
    if not url.strip():
        url = "https://www.youtube.com/watch?v=FtutLA63Cp8"
        
    os.makedirs('./media/video', exist_ok=True)
    ydl_opts: dict[str, Any] = {
        'format': 'best[ext=mp4]/best', 
        'outtmpl': './media/video/vid.mp4',
        'overwrites': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def join_2d_array(array: list[list[str]]) -> str:
    return '\n'.join(''.join(row) for row in array) + '\n'