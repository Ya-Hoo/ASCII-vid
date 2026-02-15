import cv2
import time
import ctypes
import os
import tkinter as tk
from tkinter import font as tkfont
import numpy as np
from PIL import Image, ImageTk
from functions import download_media, join_2d_array
import comtypes.client

class AsciiPlayer:
    def __init__(self):
        self.window = tk.Tk()
        self.window.state('zoomed')
        self.window.title("Gemini ASCII Player - Sync Mode")
        self.window.configure(bg='black')

        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            self.titleH = ctypes.windll.user32.GetSystemMetrics(4)
        except:
            self.titleH = 30

        # Windows Media Player Engine
        try:
            self.wmp = comtypes.client.CreateObject("WMPlayer.OCX")
        except:
            self.wmp = None

        self.density = np.array(['@@', '$@', '$$', '#$', '##', '*#', '**', '!*', '!!', 
                                '=!', '==', ';=', ';;', ':;', '::', '~:', '~~', '-~', 
                                '--', ',-', ',,', '.,', '..', ' .', '  '])
        self.pixel_factor = len(self.density) / 256

        self.window.columnconfigure(0, weight=10)
        self.window.columnconfigure(1, weight=1)
        self.window.rowconfigure(0, weight=1)

        self.ascii_font = tkfont.Font(family='Courier', size=18)
        self.char_w = self.ascii_font.measure('A') 
        self.char_h = self.ascii_font.metrics('linespace')

        self.label = tk.Text(self.window, font=self.ascii_font, bg='black', 
                             fg='white', bd=0, wrap=tk.NONE)
        self.label.grid(row=0, column=0, sticky="nsew")

        self.canvas = tk.Canvas(self.window, bg='#111', highlightthickness=0)
        self.canvas.grid(row=0, column=1, sticky="nsew")

        self.vid = None
        self.frame_ms = 0
        self.start_time = 0
        self.audio_started = False
        self.window.protocol("WM_DELETE_WINDOW", self.cleanup)

    def start(self):
        print("================ CHOOSE VIDEO SOURCE ================")
        choice = input("1: YouTube | 2: Camera | 3: Local File\nChoice: ")
        video_source = os.path.abspath('./media/video/vid.mp4')
        
        if choice == '1':
            download_media(input("YouTube Link: "))
        elif choice == '2':
            video_source = 0 
        elif choice == '3':
            pass 

        self.vid = cv2.VideoCapture(video_source if choice != '2' else 0)
        fps = self.vid.get(cv2.CAP_PROP_FPS) or 30
        self.frame_ms = 1000 / fps

        # Load audio but don't play yet
        if choice != '2' and self.wmp:
            self.wmp.URL = video_source
            self.wmp.settings.mute = True # Mute while buffering
            self.wmp.controls.play()

        self.window.update_idletasks()
        
        # Capture the absolute start time
        self.start_time = time.time()
        self.update_loop()
        self.window.mainloop()

    def update_loop(self):
        if not self.vid or not self.vid.isOpened():
            return

        success, frame = self.vid.read()
        if not success:
            self.cleanup()
            return

        loop_start = time.time()
        orig_h, orig_w = frame.shape[:2]

        # UI Measurements
        avail_w = self.label.winfo_width()
        avail_h = self.label.winfo_height()
        char_w_limit = (avail_w - 4) // self.char_w
        char_h_limit = (avail_h - 4) // self.char_h

        # Scaling
        ratio_w = (char_w_limit / 2.0) / orig_w
        ratio_h = char_h_limit / orig_h
        scale = min(ratio_w, ratio_h)
        target_w = max(1, int(orig_w * scale))
        target_h = max(1, int(orig_h * scale))

        # ASCII Processing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (target_w, target_h), interpolation=cv2.INTER_CUBIC)
        indices = (resized * self.pixel_factor).astype(int).clip(0, len(self.density)-1)
        ascii_text = join_2d_array(self.density[indices])

        self.label.delete(1.0, tk.END)
        self.label.insert(tk.END, ascii_text)

        # Preview Update
        canv_w = self.canvas.winfo_width()
        if canv_w > 10:
            canv_h = int(orig_h * (canv_w / orig_w))
            small = cv2.resize(frame, (canv_w, canv_h), interpolation=cv2.INTER_CUBIC)
            img = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(small, cv2.COLOR_BGR2RGB)))
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, image=img, anchor=tk.NW)
            self.canvas.image = img

        # --- SYNC LOGIC ---
        # Calculate where the video is currently in "real time"
        current_video_pos = self.vid.get(cv2.CAP_PROP_POS_MSEC)
        
        if not self.audio_started and current_video_pos > 0:
            # Sync the audio to the video's current position
            if self.wmp:
                self.wmp.controls.currentPosition = current_video_pos / 1000.0
                self.wmp.settings.mute = False
            self.audio_started = True

        # Calculate delay for next frame
        elapsed = (time.time() - loop_start) * 1000
        delay = max(0, int(self.frame_ms - elapsed))
        
        try:
            self.window.after(delay, self.update_loop)
        except:
            pass

    def cleanup(self):
        if self.vid:
            self.vid.release()
        if self.wmp:
            self.wmp.controls.stop()
        try:
            self.window.quit()
            self.window.destroy()
        except:
            pass

if __name__ == "__main__":
    app = AsciiPlayer()
    app.start()