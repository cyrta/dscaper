from fastapi import APIRouter
from scaper.dscaper_datatypes import TimelineCreateDTO, DscaperBackground, DscaperEvent, DscaperGenerate, DscaperWebResponse
from scaper import dscaper

url_prefix = '/api/v1/timeline'
api_router = APIRouter(prefix=url_prefix)
timeline_service = dscaper.Dscaper()


@api_router.post("/{name}")
async def create_timeline(name: str, properties: TimelineCreateDTO):
    """Create a new timeline.
    :return: A response indicating the timeline was created.
    """
    print(f"Creating timeline with name: {name} and properties: {properties}")
    response = timeline_service.create_timeline(name, properties)
    return DscaperWebResponse(response)


@api_router.post("/{name}/background")
async def add_background_to_timeline(name: str, properties: DscaperBackground):
    """Add a background to the timeline.
    :return: A response indicating the background was added.
    """
    response = timeline_service.add_background(name, properties)
    return DscaperWebResponse(response)


@api_router.post("/{name}/event")
async def add_event_to_timeline(name: str, properties: DscaperEvent):
    """Add an event to the timeline.
    :return: A response indicating the event was added.
    """
    response = timeline_service.add_event(name, properties)
    return DscaperWebResponse(response)


@api_router.post("/{name}/generate")
async def generate_timeline(name: str, properties: DscaperGenerate):
    """Generate the timeline.
    :return: A response indicating the timeline was generated.
    """
    response = timeline_service.generate_timeline(name, properties)
    return DscaperWebResponse(response)


@api_router.get("/")
async def list_timelines():
    """List all timelines.
    :return: A list of timelines.
    """
    response = timeline_service.list_timelines()
    return DscaperWebResponse(response)


@api_router.get("/{name}/background")
async def list_backgrounds(name: str):
    """List all backgrounds in the timeline.
    :return: A list of backgrounds.
    """
    response = timeline_service.list_backgrounds(name)
    return DscaperWebResponse(response)


@api_router.get("/{name}/event")
async def list_events(name: str):
    """List all events in the timeline.
    :return: A list of events.
    """
    response = timeline_service.list_events(name)
    return DscaperWebResponse(response)


@api_router.get("/{name}/generate")
async def get_generated_timeline(name: str):
    """Get the generated timeline.
    :return: The generated timeline.
    """
    response = timeline_service.get_generated_timelines(name)
    return DscaperWebResponse(response)

@api_router.get("/{name}/generate/{generate_id}")
async def get_generated_timeline_by_id(name: str, generate_id: str):
    """Get the generated timeline by ID.
    :return: The generated timeline.
    """
    response = timeline_service.get_generated_timeline_by_id(name, generate_id)
    return DscaperWebResponse(response)

@api_router.get("/{name}/generate/{generate_id}/{file_name}")
async def get_generated_file(name: str, generate_id: str, file_name: str):
    """Get a generated file by name.
    :return: The generated file.
    """
    response = timeline_service.get_generated_file(name, generate_id, file_name)
    return DscaperWebResponse(response)