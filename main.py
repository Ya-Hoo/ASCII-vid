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
        self.window.title("ASCII Player")
        self.window.configure(bg='black')

        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

        try:
            self.wmp = comtypes.client.CreateObject("WMPlayer.OCX")
        except:
            self.wmp = None

        self.density = np.array(['@@', '$@', '$$', '#$', '##', '*#', '**', '!*', '!!', 
                                '=!', '==', ';=', ';;', ':;', '::', '~:', '~~', '-~', 
                                '--', ',-', ',,', '.,', '..', ' .', '  '])
        self.pixel_factor = len(self.density) / 256

        # Layout Setup
        self.window.columnconfigure(0, weight=10)
        self.window.columnconfigure(1, weight=1)
        self.window.rowconfigure(0, weight=1)

        self.ascii_font = tkfont.Font(family='Courier', size=18)
        self.char_w = self.ascii_font.measure('A') 
        self.char_h = self.ascii_font.metrics('linespace')

        self.label = tk.Text(self.window, font=self.ascii_font, bg='black', 
                             fg='white', bd=0, wrap=tk.NONE)
        self.label.grid(row=0, column=0, sticky="nsew")

        # Preview Sidebar
        self.canvas = tk.Canvas(self.window, bg='#111', highlightthickness=0)
        self.canvas.grid(row=0, column=1, sticky="nsew")

        self.vid = None
        self.frame_ms = 0
        self.window.protocol("WM_DELETE_WINDOW", self.cleanup)

    def start(self):
        print("================ CHOOSE VIDEO SOURCE ================")
        choice = input("1: YouTube | 2: Camera | 3: Local File\nChoice: ")
        video_source = os.path.abspath('./media/video/vid.mp4')
        
        if choice == '1':
            url = input("YouTube Link (Enter for Bad Apple): ")
            download_media(url)
        elif choice == '2':
            video_source = 0 
        elif choice == '3':
            pass 

        self.vid = cv2.VideoCapture(video_source if choice != '2' else 0)
        fps = self.vid.get(cv2.CAP_PROP_FPS) or 30
        self.frame_ms = 1000 / fps

        if choice != '2' and self.wmp:
            self.wmp.URL = video_source
            self.wmp.controls.play()

        self.window.update_idletasks()
        self.update_loop()
        self.window.mainloop()

    def update_loop(self):
        if not self.vid or not self.vid.isOpened():
            return

        start_time = time.time()
        success, frame = self.vid.read()
        if not success:
            self.cleanup()
            return

        # AUDIO SYNC
        sync_delay_mod = 0
        if self.wmp:
            vid_ts = self.vid.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            aud_ts = self.wmp.controls.currentPosition
            
            # If video is lagging behind audio, reduce delay to speed up
            if vid_ts < aud_ts - 0.05:
                sync_delay_mod = -5 
            # If video is too far ahead, increase delay to wait
            elif vid_ts > aud_ts + 0.05:
                sync_delay_mod = 5

        # Render ASCII
        orig_h, orig_w = frame.shape[:2]
        avail_w = self.label.winfo_width()
        avail_h = self.label.winfo_height()
        
        char_w_limit = (avail_w - 4) // self.char_w
        char_h_limit = (avail_h - 4) // self.char_h

        scale = min((char_w_limit / 2.0) / orig_w, char_h_limit / orig_h)
        tw, th = max(1, int(orig_w * scale)), max(1, int(orig_h * scale))

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (tw, th), interpolation=cv2.INTER_NEAREST)
        indices = (resized * self.pixel_factor).astype(int).clip(0, len(self.density)-1)
        
        self.label.delete(1.0, tk.END)
        self.label.insert(tk.END, join_2d_array(self.density[indices]))

        # Sidebar Preview Update
        canv_w = self.canvas.winfo_width()
        if canv_w > 10:
            canv_h = int(orig_h * (canv_w / orig_w))
            small = cv2.resize(frame, (canv_w, canv_h), interpolation=cv2.INTER_LINEAR)
            img = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(small, cv2.COLOR_BGR2RGB)))
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, image=img, anchor=tk.NW)
            self.canvas.image = img  # type: ignore

        # Timing with Sync Modifier
        elapsed = (time.time() - start_time) * 1000
        delay = max(1, int(self.frame_ms - elapsed + sync_delay_mod))
        
        try:
            self.window.after(delay, self.update_loop)
        except:
            pass

    def cleanup(self):
        if self.vid: self.vid.release()
        if self.wmp: self.wmp.controls.stop()
        try: self.window.destroy()
        except: pass

if __name__ == "__main__":
    app = AsciiPlayer()
    app.start()