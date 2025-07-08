from typing import Union

from fastapi import FastAPI
from web.api.audio_api import api_router as audio_api_router
from web.api.timeline_api import api_router as timeline_api_router

app = FastAPI()

# Include the audio API router
app.include_router(audio_api_router)
# Include the timeline API router
app.include_router(timeline_api_router)


@app.get("/")
def read_root():
    return {"API": "Welcome to the Scaper API"}