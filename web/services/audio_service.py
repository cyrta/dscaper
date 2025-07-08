from web.services.web_models import AudioMetadata, AudioMetadataSaveDTO
from typing import Any, Annotated
from fastapi import APIRouter, File, Form, Response, status
import uuid
import os
import time
import soundfile

audio_path = os.path.join(os.getcwd(), "data", "audio")
audio_metadata_path = os.path.join(os.getcwd(), "data", "audio_metadata")

def store_audio(file: Annotated[bytes, File()], metadata: AudioMetadataSaveDTO, update: bool = False):
    """
    Store audio file and its metadata.
    
    :param file: The audio file to be stored.
    :param metadata: Metadata for the audio file.
    :return: An AudioMetadata object containing the stored audio's metadata.
    """
    m = metadata
    # check if file is empty
    if len(file) == 0:
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content="File is empty")
    # filename and path
    file_path = os.path.join(audio_path, m.library, m.label)
    audio_destination = os.path.join(file_path, m.filename)
    base, ext = os.path.splitext(m.filename)
    metadata_destination = os.path.join(file_path, base + ".json")
    # check if the file already exists
    if os.path.exists(audio_destination) and not update:
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content=f"File already exists in. Use PUT to update it.")
    elif not os.path.exists(audio_destination) and update:
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content=f"File does not exist. Use POST to create it.")
    # create the directory if it does not exist
    os.makedirs(file_path, exist_ok=True)
    # save the file to the audio path
    with open(audio_destination, "wb") as f:
        f.write(file)
    # check if audio file is valid
    try:
        duration = soundfile.info(audio_destination).duration
    except RuntimeError as e:
        # delete the file if it is not valid
        os.remove(audio_destination)
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content=f"Invalid audio file: {str(e)}")
    # create the metadata object
    file_id = str(uuid.uuid4())
    timestamp = int(time.time())
    metadata_obj = AudioMetadata(id=file_id, library=m.library, label=m.label, filename=m.filename, foreground=m.foreground, 
                             sandbox=m.sandbox, timestamp=timestamp, duration=duration)
    # save the metadata to the audio metadata path
    with open(metadata_destination, "w") as f:
        f.write(metadata_obj.model_dump_json())
    # return the metadata object
    return metadata_obj