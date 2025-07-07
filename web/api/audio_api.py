import time
from fastapi import APIRouter, Response, status, File, Form
from pydantic import BaseModel
from typing import Any, Annotated
import uuid
import os
import soundfile


url_prefix = '/api/v1/audio'
api_router = APIRouter(prefix=url_prefix)

audio_path = os.path.join(os.getcwd(), "data", "audio")
audio_metadata_path = os.path.join(os.getcwd(), "data", "audio_metadata")


class AudioMetadataCreateDTO(BaseModel):
    project: str
    label: str
    filename: str
    foreground: bool = True
    sandbox: str = "{}"  # JSON string

class AudioMetadata(BaseModel):
    id: str # set by the server
    project: str
    label: str
    filename: str
    foreground: bool
    sandbox: str # JSON string
    timestamp: int # set by the server
    duration: float # set by the server


@api_router.post("/")
# cant use AudioMetadataCreateDTO because you can't also declare Body fields that you expect to 
# receive as JSON, as the request will have the body encoded using multipart/form-data instead 
# of application/json (see fastapi docs)
async def store_audio(
                      file: Annotated[bytes, File()], 
                      project: Annotated[str, Form()],
                      label: Annotated[str, Form()],
                      filename: Annotated[str, Form()],
                      foreground: Annotated[bool, Form()],
                      sandbox: Annotated[str, Form()]):
    # check if file is empty
    if len(file) == 0:
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content="File is empty")
    # generate a unique ID for the file
    file_id = uuid.uuid4().hex
    # save the file to the audio path
    base, ext = os.path.splitext(filename)
    temp_file = os.path.join(audio_path, file_id+ext) 
    with open(temp_file, "wb") as f:
        f.write(file)
    # check if audio file is valid
    try:
        duration = soundfile.info(temp_file).duration
    except RuntimeError as e:
        # delete the file if it is not valid
        os.remove(temp_file)
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content=f"Invalid audio file: {str(e)}")
    # create the metadata object
    timestamp = int(time.time())
    metadata = AudioMetadata(id=file_id, project=project, label=label, filename=filename, foreground=foreground, 
                             sandbox=sandbox, timestamp=timestamp, duration=duration)
    # save the metadata to the audio metadata path
    metadata_file = os.path.join(audio_metadata_path, file_id + ".json")
    with open(metadata_file, "w") as f:
        f.write(metadata.model_dump_json())
    # return the metadata object
    return metadata
    