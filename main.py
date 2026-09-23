from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
import edge_tts
import requests
import random
import os
import subprocess
import imageio_ffmpeg
from PIL import Image

app = FastAPI()

PEXELS_API_KEY = "AzR2SYG5DNdPvu4fTJYyY1piJlPHKkaFXzqJM2y0uqKIw5YlVAHlvAQt"

@app.get("/")
def read_root():
    return {"status": "Video & TTS Server Live"}

@app.get("/tts")
async def tts(text: str, voice: str = "hi-IN-MadhurNeural"):
    communicate = edge_tts.Communicate(text, voice)
    output_file = "output.mp3"
    await communicate.save(output_file)
    with open(output_file, "rb") as f:
        data = f.read()
    return Response(content=data, media_type="audio/mpeg")

@app.get("/video")
async def generate_video(text: str, voice: str = "hi-IN-MadhurNeural", mode: str = "vertical"):
    audio_path = "temp_audio.mp3"
    img_path = "temp_img.jpg"
    output_video = "output_video.mp4"

    # Purani files saf karein
    for f in [audio_path, img_path, output_video]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception:
                pass

    # 1. TTS Audio generate karein
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(audio_path)
    
    # 2. Aspect Ratio tay karein
    if mode == "horizontal":
        pexels_orientation = "landscape"
        target_size = (1920, 1080)
    else:
        pexels_orientation = "portrait"
        target_size = (1080, 1920)

    # 3. Pexels se Image download karein
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/v1/search?query=nature background&orientation={pexels_orientation}&per_page=15"
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200 and res.json().get("photos"):
            photos = res.json()["photos"]
            img_url = random.choice(photos)["src"]["large2x"]
            img_data = requests.get(img_url, timeout=10).content
            with open(img_path, "wb") as f:
                f.write(img_data)
        else:
            img = Image.new('RGB', target_size, color=(20, 20, 35))
            img.save(img_path)
    except Exception:
        img = Image.new('RGB', target_size, color=(20, 20, 35))
        img.save(img_path)

    # 4. Image Resize karein
    try:
        img = Image.open(img_path).convert("RGB")
        img = img.resize(target_size)
        img.save(img_path)
    except Exception:
        img = Image.new('RGB', target_size, color=(20, 20, 35))
        img.save(img_path)

    # 5. Fast FFmpeg se Video (.mp4) banayein
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe,
        "-y",
        "-loop", "1",
        "-i", img_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_video
    ]
    
    subprocess.run(cmd, check=True)

    return FileResponse(output_video, media_type="video/mp4")
