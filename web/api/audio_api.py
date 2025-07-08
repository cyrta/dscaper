import time
from fastapi import APIRouter, Response, status, File, Form
from pydantic import BaseModel
from typing import Any, Annotated
import uuid
import os
import soundfile
from web.services.web_models import AudioMetadata, AudioMetadataSaveDTO
import web.services.audio_service as audio_service

url_prefix = '/api/v1/audio'
api_router = APIRouter(prefix=url_prefix)


@api_router.post("/{library}/{label}/{filename}")
# cant use AudioMetadataCreateDTO because you can't also declare Body fields that you expect to 
# receive as JSON, as the request will have the body encoded using multipart/form-data instead 
# of application/json (see fastapi docs)
async def add_audio(library: str, 
                      label: str, 
                      filename: str,
                      file: Annotated[bytes, File()], 
                      foreground: Annotated[bool, Form()],
                      sandbox: Annotated[str, Form()]):
    """Store audio file and its metadata.
    :param library: The library to store the audio in.
    :param label: The label for the audio file.
    :param filename: The name of the audio file.
    :param file: The audio file to be stored.
    :param foreground: Whether the audio is a foreground sound.
    :param sandbox: JSON string containing sandbox data.
    :return: An AudioMetadata object containing the stored audio's metadata.
    Exceptions:
        - 400: If the file is empty or invalid.
        - 400: If the file already exists.
    """
    metadata = AudioMetadataSaveDTO(
        library=library,
        label=label,
        filename=filename,
        foreground=foreground,
        sandbox=sandbox
    )

    return audio_service.store_audio(file, metadata)

    
@api_router.put("/{library}/{label}/{filename}")
async def update_audio(library: str, 
                      label: str, 
                      filename: str,
                      file: Annotated[bytes, File()], 
                      foreground: Annotated[bool, Form()],
                      sandbox: Annotated[str, Form()]):
    """Update audio file and its metadata.
    see add_audio for parameter descriptions.
    :return: An AudioMetadata object containing the updated audio's metadata.
    Exceptions:
        - 400: If the file is empty or invalid.
        - 400: If the file does not exist.
    """
    metadata = AudioMetadataSaveDTO(
        library=library,
        label=label,
        filename=filename,
        foreground=foreground,
        sandbox=sandbox
    )

    return audio_service.store_audio(file, metadata, update=True)


@api_router.get("/{library}/{label}/{filename}")
async def get_audio(library: str, label: str, filename: str):
    """Get audio metadata or the audio file itself.
    :param library: The library of the audio file.
    :param label: The label of the audio file.
    :param filename: The name of the audio file or the metadata file.
    :return: An AudioMetadata object containing the audio's metadata or the audio file itself.
    Exceptions:
        - 404: If the audio file does not exist.
    """
    return audio_service.read_audio(library, label, filename)
    
