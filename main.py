from fastapi import FastAPI, Response
import edge_tts
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "AI Voice Generator Server Live"}

@app.get("/tts")
async def tts(text: str, voice: str = "hi-IN-MadhurNeural"):
    output_file = "output.mp3"
    
    if os.path.exists(output_file):
        try:
            os.remove(output_file)
        except Exception:
            pass

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)
    
    with open(output_file, "rb") as f:
        data = f.read()
        
    return Response(content=data, media_type="audio/mpeg")
