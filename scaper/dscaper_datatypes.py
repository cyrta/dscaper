from typing import Any, Optional
from pydantic import BaseModel, Json


class DscaperAudio(BaseModel):
    id: str = "" # set by the server
    library: str
    label: str
    filename: str
    sandbox: str = "{}"# JSON string
    timestamp: int = 0# set by the server
    duration: float = 0# set by the server

class DscaperTimeline(BaseModel):
    id: str = "" # set by the server
    name: str 
    duration: float = 0  
    description: str = ""
    sandbox: str = "{}"  # JSON string
    timestamp: int = 0# set by the server

class DscaperTimelines(BaseModel):
    timelines: list[DscaperTimeline] = []
   
class DscaperBackground(BaseModel):
    library: str
    label: list[str] = ['choose', '[]']
    source_file: list[str] = ['choose', '[]']
    source_time: list[str] = ['const', '0']
    id: Optional[str] = None # set by the server

class DscaperBackgrounds(BaseModel):
    backgrounds: list[DscaperBackground] = []

class DscaperEvent(BaseModel):
    library: str
    label: list[str] = ['choose', '[]']
    source_file: list[str] = ['choose', '[]']
    source_time: list[str] = ['const', '0']
    event_time: list[str] = ['const', '0']
    event_duration: Optional[list[str]] = None # if not set, will use duration of the audio file or default to 5 seconds
    snr: list[str] = ['const', '0']
    pitch_shift: Optional[list[str]] = None
    time_stretch: Optional[list[str]] = None
    position: Optional[str] = None
    speaker: Optional[str] = None
    text: Optional[str] = None
    id: Optional[str] = None # set by the server

class DscaperEvents(BaseModel):
    events: list[DscaperEvent] = []

class DscaperGenerate(BaseModel):
    seed: int = 0
    ref_db: int = -20
    reverb: float = 0.0
    save_isolated_events: bool = False
    save_isolated_positions: bool = False
    id: Optional[str] = None # set by the server
    timestamp: int = 0 # set by the server
    generated_files: list[str] = []  # List of generated audio files, set by the server

class DscaperGenerations(BaseModel):
    generations: list[DscaperGenerate] = []

class DscaperApiResponse(BaseModel):
    status: str
    status_code: int
    content: Optional[Any] = None  # Optional response message
    media_type: Optional[str] = "text/plain"  # Optional type field for response categorization

class DscaperJsonResponse(BaseModel):
    status: str = "success"
    status_code: int = 200
    content: Json[Any]
    media_type: str = "application/json"




      