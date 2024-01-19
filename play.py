import youtube_dl
import os, cv2

link = "https://www.youtube.com/watch?v=UkgK8eUdpAo"

def download_video(url: str) -> None:
    ydl_opts = {
        'format':'best',
        'outtmpl': '/video/vid.mp4'
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        
        
# convert to ascii
def toASCII(RGB):
    # Source https://stackoverflow.com/a/17619494
    R, G, B = tuple(map(lambda x: x / 255, RGB))
    C_linear = 0.2126*R + 0.7152*G + 0.0722*B
    if C_linear <= 0.0031308:
        gray = C_linear * 12.92
    else:
        gray = 1.055 * pow(C_linear, 1/2.4) -0.055
    
    density = " .:-=+*#%@"
    return density[int(gray * len(density))]

if not os.path.exists('./video/vid.mp4'):
    download_video(link)

cap = cv2.VideoCapture('./video/vid.mp4')
time_count = 0

while cap.isOpened():
    cap.set(0, time_count)
    success, frame = cap.read()
    if success:
        h, w, _ = frame.shape
        frame = cv2.resize(frame, (75, int(h/w*75)))
        H, W, _ = frame.shape
        
        pic = ""
        
        for y in range(H):
            for x in range(W):
                pic += toASCII(frame[y, x])
            pic += "\n"
            
        print(pic, flush=True)
            
    time_count += 60