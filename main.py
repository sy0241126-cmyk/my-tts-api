from fastapi import FastAPI, Response
import edge_tts

app = FastAPI()

@app.get("/tts")
async def generate_tts(text: str, voice: str = "hi-IN-MadhurNeural"):
    try:
        communicate = edge_tts.Communicate(text, voice)
        audio_bytes = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_bytes += chunk["data"]
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except Exception as e:
        return Response(content=str(e), status_code=500)
