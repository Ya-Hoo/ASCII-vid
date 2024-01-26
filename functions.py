from random import randint
from yt_dlp import YoutubeDL

import numpy as np


def download_video(url: str) -> None:
    # download vid
    ydl_opts = {
        'format':'best',
        'outtmpl': '/media/video/vid.mp4'
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    # download sound
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '/media/audio/aud.mp3'
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


# joining generated char together
def join1D(array):
    return ''.join(array) + '\n'


def join2D(array):
    return ''.join([join1D(row) for row in array])