from fastapi import APIRouter, File, Form
from typing import Annotated
from web.services.web_models import AudioMetadataSaveDTO, DscaperWebResponse
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
        sandbox=sandbox
    )
    response = audio_service.store_audio(file, metadata)
    return DscaperWebResponse(response)  

    
@api_router.put("/{library}/{label}/{filename}")
async def update_audio(library: str, 
                      label: str, 
                      filename: str,
                      file: Annotated[bytes, File()], 
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
        sandbox=sandbox
    )
    response = audio_service.store_audio(file, metadata, update=True)
    return DscaperWebResponse(response) 


@api_router.get("/")
async def get_libraries():
    """Get a list of all audio libraries.
    :return: A list of library names.
    """
    response = audio_service.get_libraries()
    return DscaperWebResponse(response) 


@api_router.get("/{library}")
async def get_labels(library: str):
    """Get a list of all labels in a specific audio library.
    :param library: The library to get labels from.
    :return: A list of label names in the specified library.
    Exceptions:
        - 404: If the library does not exist.
    """
    response = audio_service.get_labels(library)
    return DscaperWebResponse(response) 


@api_router.get("/{library}/{label}")
async def get_filenames(library: str, label: str):
    """Get a list of all filenames in a specific audio label.
    :param library: The library to get filenames from.
    :param label: The label to get filenames from.
    :return: A list of filenames in the specified label.
    Exceptions:
        - 404: If the library or label does not exist.
    """
    response = audio_service.get_filenames(library, label)
    return DscaperWebResponse(response) 


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
    response = audio_service.read_audio(library, label, filename)
    return DscaperWebResponse(response) 
    
