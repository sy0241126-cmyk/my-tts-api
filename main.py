from fastapi import FastAPI, HTTPException
import requests
import os
from fastapi.responses import RedirectResponse

app = FastAPI()

# Pexels API Key jo aapne abhi banayi hai
PEXELS_API_KEY = "AzR2SYG5DNdPvu4fTJYyY1piJlPHKkaFXzqJM2y0uqKIw5YlVAHlvAQt"

@app.get("/")
def home():
    return {"message": "AI Voice & Script Studio API is Running!"}

# 1. Pexels Photo Search Endpoint
@app.get("/search-photos")
def search_photos(query: str):
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=5"
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Pexels API se data laane me samasya aayi")
    
    data = response.json()
    photos = [photo["src"]["large"] for photo in data.get("photos", [])]
    
    return {"query": query, "photos": photos}

# 2. Aapka Purana Edge-TTS / Audio Endpoint yahan rahega (Agar aapne alag se rakha hai)
