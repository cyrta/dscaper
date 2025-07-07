from typing import Union

from fastapi import FastAPI
from web.api.audio_api import api_router as audio_api_router

app = FastAPI()

# Include the audio API router
app.include_router(audio_api_router)


@app.get("/")
def read_root():
    return {"API": "Welcome to the Scaper API"}