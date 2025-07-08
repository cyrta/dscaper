from pydantic import BaseModel


class AudioMetadataSaveDTO(BaseModel):
    library: str
    label: str
    filename: str
    foreground: bool = True
    sandbox: str = "{}"  # JSON string

class AudioMetadata(BaseModel):
    id: str # set by the server
    library: str
    label: str
    filename: str
    foreground: bool
    sandbox: str # JSON string
    timestamp: int # set by the server
    duration: float # set by the server
