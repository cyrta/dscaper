from pydantic import BaseModel
from typing import Union
from fastapi import Response
import json
from scaper.dscaper_datatypes import DscaperJsonResponse, DscaperApiResponse


class TimelineCreateDTO(BaseModel):
    duration: float = 0 
    description: str = ""
    sandbox: str = "{}"  # JSON string

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