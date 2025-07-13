from pydantic import BaseModel, Json
from typing import Any, Union
from fastapi import Response
import json



class AudioMetadataSaveDTO(BaseModel):
    library: str
    label: str
    filename: str
    sandbox: str = "{}"  # JSON string

class AudioMetadata(BaseModel):
    id: str # set by the server
    library: str
    label: str
    filename: str
    sandbox: str # JSON string
    timestamp: int # set by the server
    duration: float # set by the server

class TimelineCreateDTO(BaseModel):
    duration: float = 0 
    description: str = ""
    sandbox: str = "{}"  # JSON string

class DscaperTimeline(BaseModel):
    id: str # set by the server
    name: str 
    duration: float = 0  
    description: str = ""
    sandbox: str = "{}"  # JSON string
    timestamp: int # set by the server

class DscaperTimelines(BaseModel):
    timelines: list[DscaperTimeline] = []
   
class DscaperBackground(BaseModel):
    library: str
    label: list[str] = ['choose', '[]']
    source_file: list[str] = ['choose', '[]']
    source_time: list[str] = ['const', '0']
    id: str | None = None # set by the server

class DscaperBackgrounds(BaseModel):
    backgrounds: list[DscaperBackground] = []

class DscaperEvent(BaseModel):
    library: str
    label: list[str] = ['choose', '[]']
    source_file: list[str] = ['choose', '[]']
    source_time: list[str] = ['const', '0']
    event_time: list[str] = ['const', '0']
    event_duration: list[str] = ['const', '5']
    snr: list[str] = ['const', '0']
    pitch_shift: list[str] | None = None
    time_stretch: list[str] | None = None
    event_type: str | None = None
    id: str | None = None # set by the server

class DscaperEvents(BaseModel):
    events: list[DscaperEvent] = []

class DscaperGenerate(BaseModel):
    seed: int = 0
    ref_db: int = -20
    reverb: float = 0.0
    save_isolated_events: bool = False
    save_isolated_eventtypes: bool = False
    id: str | None = None # set by the server
    timestamp: int = 0 # set by the server
    generated_files: list[str] = []  # List of generated audio files, set by the server

class DscaperGenerations(BaseModel):
    generations: list[DscaperGenerate] = []

class DscaperApiResponse(BaseModel):
    status: str
    status_code: int
    content: Any | None = None  # Optional response message
    media_type: str | None = "text/plain"  # Optional type field for response categorization

class DscaperJsonResponse(BaseModel):
    status: str = "success"
    status_code: int = 200
    content: Json[Any]
    media_type: str = "application/json"

class DscaperWebResponse(Response):
    def __init__(self, api_response: Union[DscaperJsonResponse, DscaperApiResponse]):
        if api_response.media_type is "application/json":
            content = json.dumps(api_response.content)
        else:
            content = api_response.content
        super().__init__(
            content=content,
            status_code=api_response.status_code,
            media_type=api_response.media_type
        )


      