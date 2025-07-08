from fastapi import APIRouter
from web.services.web_models import TimelineCreateDTO, DscaperBackground
import web.services.timeline_service as timeline_service

url_prefix = '/api/v1/timeline'
api_router = APIRouter(prefix=url_prefix)



@api_router.post("/{name}")
async def create_timeline(name: str, properties: TimelineCreateDTO):
    """Create a new timeline.
    :return: A response indicating the timeline was created.
    """
    print(f"Creating timeline with name: {name} and properties: {properties}")
    return timeline_service.create_timeline(name, properties)
    # Placeholder for timeline creation logic
    
@api_router.post("/{name}/background")
async def add_background_to_timeline(name: str, properties: DscaperBackground):
    """Add a background to the timeline.
    :return: A response indicating the background was added.
    """
    print(f"Adding background to timeline {name} with properties: {properties}")
    return timeline_service.add_background(name, properties)
    # Placeholder for adding background logic