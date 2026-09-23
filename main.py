from fastapi import FastAPI, HTTPException
import requests
from deep_translator import GoogleTranslator

app = FastAPI()

PEXELS_API_KEY = "AzR2SYG5DNdPvu4fTJYyY1piJlPHKkaFXzqJM2y0uqKIw5YlVAHlvAQt"

@app.get("/")
def home():
    return {"message": "Hindi Script Photo Finder API is Running!"}

@app.get("/search-photos")
def search_photos(query: str):
    try:
        # 1. Hindi query ko automatically English me translate karna
        english_query = GoogleTranslator(source='auto', target='en').translate(query)
    except Exception as e:
        english_query = query # Agar translation me error aaye toh wahi query bhej do
    
    # 2. Pexels API par English query bhejna
    url = f"https://api.pexels.com/v1/search?query={english_query}&per_page=5"
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Pexels API se data laane me samasya aayi")
    
    data = response.json()
    photos = [photo["src"]["large"] for photo in data.get("photos", [])]
    
    return {"hindi_query": query, "english_query": english_query, "photos": photos}
