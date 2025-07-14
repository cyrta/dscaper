from fastapi import APIRouter
from scaper.dscaper_datatypes import DscaperTimeline, DscaperBackground, DscaperEvent, DscaperGenerate
from scaper import dscaper
from web.api.datatypes import TimelineCreateDTO, DscaperWebResponse


url_prefix = '/api/v1/timeline'
api_router = APIRouter(prefix=url_prefix)
timeline_service = dscaper.Dscaper()


@api_router.post("/{timeline_name}")
async def create_timeline(timeline_name: str, properties: TimelineCreateDTO):
    """Create a new timeline.
    :return: A response indicating the timeline was created.
    """
    print(f"Creating timeline with name: {timeline_name} and properties: {properties}")
    props = DscaperTimeline(name=timeline_name, duration=properties.duration, description=properties.description, sandbox=properties.sandbox)
    response = timeline_service.create_timeline(props)
    return DscaperWebResponse(response)


@api_router.post("/{timeline_name}/background")
async def add_background_to_timeline(timeline_name: str, properties: DscaperBackground):
    """Add a background to the timeline.
    :return: A response indicating the background was added.
    """
    response = timeline_service.add_background(timeline_name, properties)
    return DscaperWebResponse(response)


@api_router.post("/{timeline_name}/event")
async def add_event_to_timeline(timeline_name: str, properties: DscaperEvent):
    """Add an event to the timeline.
    :return: A response indicating the event was added.
    """
    response = timeline_service.add_event(timeline_name, properties)
    return DscaperWebResponse(response)


@api_router.post("/{timeline_name}/generate")
async def generate_timeline(timeline_name: str, properties: DscaperGenerate):
    """Generate the timeline.
    :return: A response indicating the timeline was generated.
    """
    response = timeline_service.generate_timeline(timeline_name, properties)
    return DscaperWebResponse(response)


@api_router.get("/")
async def list_timelines():
    """List all timelines.
    :return: A list of timelines.
    """
    response = timeline_service.list_timelines()
    return DscaperWebResponse(response)


@api_router.get("/{timeline_name}/background")
async def list_backgrounds(timeline_name: str):
    """List all backgrounds in the timeline.
    :return: A list of backgrounds.
    """
    response = timeline_service.list_backgrounds(timeline_name)
    return DscaperWebResponse(response)


@api_router.get("/{timeline_name}/event")
async def list_events(timeline_name: str):
    """List all events in the timeline.
    :return: A list of events.
    """
    response = timeline_service.list_events(timeline_name)
    return DscaperWebResponse(response)


@api_router.get("/{timeline_name}/generate")
async def get_generated_timeline(timeline_name: str):
    """Get the generated timeline.
    :return: The generated timeline.
    """
    response = timeline_service.get_generated_timelines(timeline_name)
    return DscaperWebResponse(response)

@api_router.get("/{timeline_name}/generate/{generate_id}")
async def get_generated_timeline_by_id(timeline_name: str, generate_id: str):
    """Get the generated timeline by ID.
    :return: The generated timeline.
    """
    response = timeline_service.get_generated_timeline_by_id(timeline_name, generate_id)
    return DscaperWebResponse(response)

@api_router.get("/{timeline_name}/generate/{generate_id}/{file_name}")
async def get_generated_file(timeline_name: str, generate_id: str, file_name: str):
    """Get a generated file by name.
    :return: The generated file.
    """
    response = timeline_service.get_generated_file(timeline_name, generate_id, file_name)
    return DscaperWebResponse(response)