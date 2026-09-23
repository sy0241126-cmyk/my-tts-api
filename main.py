from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
import edge_tts
import requests
import random
import os
from PIL import Image
from moviepy.editor import ImageClip, AudioFileClip

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
    # 1. TTS Audio generate karein
    audio_path = "temp_audio.mp3"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(audio_path)
    
    # 2. Mode chuney: vertical (9:16) ya horizontal (16:9)
    if mode == "horizontal":
        pexels_orientation = "landscape"
        target_size = (1920, 1080)  # Leti Video (YouTube Long)
    else:
        pexels_orientation = "portrait"
        target_size = (1080, 1920)  # Khadi Video (Reels/Shorts)

    # 3. Pexels se Image fetch karein
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/v1/search?query=nature background&orientation={pexels_orientation}&per_page=15"
    
    img_path = "temp_img.jpg"
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200 and res.json().get("photos"):
            photos = res.json()["photos"]
            img_url = random.choice(photos)["src"]["large2x"]
            img_data = requests.get(img_url).content
            with open(img_path, "wb") as f:
                f.write(img_data)
        else:
            img = Image.new('RGB', target_size, color=(20, 20, 35))
            img.save(img_path)
    except Exception:
        img = Image.new('RGB', target_size, color=(20, 20, 35))
        img.save(img_path)

    # 4. Image ko exact resolution me resize karein
    img = Image.open(img_path).convert("RGB")
    img = img.resize(target_size)
    img.save(img_path)

    # 5. Audio + Image ko milakar Video (.mp4) banayein
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration
    
    video_clip = ImageClip(img_path).set_duration(duration)
    video_clip = video_clip.set_audio(audio_clip)
    
    output_video = "output_video.mp4"
    video_clip.write_videofile(output_video, fps=24, codec="libx264", audio_codec="aac")
    
    audio_clip.close()
    video_clip.close()

    return FileResponse(output_video, media_type="video/mp4")
