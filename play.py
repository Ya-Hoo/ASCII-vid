import yt_dlp, cv2, time
import tkinter as tk

from PIL import Image, ImageTk
from ffpyplayer.player import MediaPlayer


def download_video(url: str) -> None:
    # download vid
    ydl_opts = {
        'format':'best',
        'outtmpl': '/media/video/vid.mp4'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    # download sound
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '/media/audio/aud.mp3'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        
# convert gray --> ascii
def toASCII(gray: int) -> str:    
    return density[int(gray * pixel_factor)]


if __name__ == "__main__":
    print("================ CHOOSE VIDEO SOURCE ================")
    source = int(input("Option 1: YouTube video\nOption 2: Camera feed\nOption 3: File on system\n\nEnter choice: "))
    if source == 2:
        print("=================== CHOOSE CAMERA ===================")
        front_back = int(input("Option 1: Webcam\nOption 2: Back cam\n\nEnter choice: "))
        vid = cv2.VideoCapture(front_back-1)
    else:
        if source == 1:
            link = input("Put YouTube link: ")
            download_video(link)
        
        # configure video and audio
        vid = cv2.VideoCapture('./media/video/vid.mp4')
        audio_player: MediaPlayer
        audio_player_options = {
            'autoexit': True,
            'vn': True,
            'sn': True
        }
        audio_player = MediaPlayer('./media/audio/aud.mp3', ff_opts=audio_player_options)

    # constants
    density = ['  ', '..', ',,', '--', '~~', '::', ';;', '==', '!!', '**', '##', '$$', '@@'][::-1]
    pixel_num = len(density)
    pixel_factor = pixel_num / 256

    # create window
    window = tk.Tk()
    window.state('zoomed')
    window.title("Video in ASCII")
    screenW = window.winfo_screenwidth()
    screenH = window.winfo_screenheight()
    
    # creates two frame to divide window in 2/3
    window.columnconfigure(0, weight=7)
    window.columnconfigure(1, weight=1)
    lframe = tk.Frame(window, height=screenH)
    lframe.grid(row=0, column=0, sticky="nsew")
    lframe.columnconfigure(0, weight=1)
    lframe.rowconfigure(0, weight=1)
    rframe = tk.Frame(window, height=screenH)
    rframe.grid(row=0, column=1, sticky="nsew")
    rframe.columnconfigure(0, weight=1)
    rframe.rowconfigure(0, weight=1)
    
    # create label to put results in
    label = tk.Text(lframe, font=('courier', 8))
    label.grid(row=0, column=0, sticky="nsew")
    
    # create canvas to put original video in
    canvas = tk.Canvas(rframe, height=screenH)
    canvas.grid(row=0, column=0, sticky="nsew")
    
    # frame stats to sync vid and sound
    frame_t = 1000 / vid.get(cv2.CAP_PROP_FPS)
    frame_counter = 0
    prev_finish_t = 0.0
    accumulation = 0.0
    
    # displaying frames
    def next_frame():
        global time_count, frame_counter, prev_finish_t, accumulation
        success, frame = vid.read()
        start_t = time.time()
        h, w = len(frame), len(frame[0])
        
        # place actual video on canvas
        small_frame = cv2.resize(frame, dsize=(int(w/h*375), 375), interpolation=cv2.INTER_CUBIC)
        currentImage = Image.fromarray(cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB))
        photo = ImageTk.PhotoImage(image=currentImage)
        canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        canvas.image = photo
        
        ascii_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ascii_frame = cv2.resize(ascii_frame, dsize=(int(w/h*75), 75), interpolation=cv2.INTER_CUBIC)
        H = ascii_frame.shape[0]
        
        # where the magic happens
        pic = ""
        for y in range(H):
            pic += "".join(list(map(toASCII, ascii_frame[y]))) + "\n"
            
        label.delete(1.0, "end-1c")
        label.insert("end-1c", pic)
        
        # syncing vid and audio
        frame_counter += 1
        if success:
            finish_t = time.time()
            t_difference = frame_t - (finish_t - prev_finish_t) * 1000
            accumulation += t_difference * (frame_counter > 2)
            dt = frame_t - (finish_t - start_t) * 1000 + accumulation
            prev_finish_t = finish_t
            if dt > 0:
                window.after(int(dt), next_frame)
            else:
                window.after(0, next_frame)
        
    window.after(0, next_frame)
    window.mainloop()
    
    
