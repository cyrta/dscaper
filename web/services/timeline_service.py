from web.services.web_models import TimelineCreateDTO, DscaperTimeline, DscaperBackground, DscaperEvent
from fastapi import APIRouter, Response, status
import os
import uuid
import time

timeline_basedir = os.path.join(os.getcwd(), "data", "timeline")


def create_timeline(name: str, properties: TimelineCreateDTO):
    """Create a new timeline.
    
    :param name: The name of the timeline.
    :param properties: Properties for the timeline.
    :return: A Timeline object containing the created timeline's metadata.
    """
    timeline_path = os.path.join(timeline_basedir, name)
    timeline_config = os.path.join(timeline_path, "timeline.json")
    # Check if the timeline already exists
    if os.path.exists(timeline_config):
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content=f"Timeline '{name}' already exists.")
    # Create the directory if it does not exist
    os.makedirs(timeline_path, exist_ok=True)
    # Create the Timeline object
    p = properties
    file_id = str(uuid.uuid4())
    timestamp = int(time.time())
    timeline = DscaperTimeline(
        id=file_id,
        name=name,
        duration=p.duration,
        seed=p.seed,
        description=p.description,
        ref_db=p.ref_db,
        sandbox=p.sandbox,
        timestamp=timestamp
    )
    # Save the timeline to a JSON file
    with open(timeline_config, "w") as f:
        f.write(timeline.model_dump_json())
    # Return the created timeline object
    return timeline
    

def add_background(name: str, properties: DscaperBackground):
    """Add a background to the timeline.
    
    :param name: The name of the timeline.
    :param properties: Properties for the background.
    :return: A DscaperBackground object containing the added background's metadata.
    Exceptions:
        - 404: If the timeline does not exist.
    """
    timeline_path = os.path.join(timeline_basedir, name)
    timeline_config = os.path.join(timeline_path, "timeline.json")
    # Check if the timeline exists
    if not os.path.exists(timeline_config):
        return Response(status_code=status.HTTP_404_NOT_FOUND, content=f"Timeline '{name}' does not exist.")
    # Create the background directory if it does not exist
    background_path = os.path.join(timeline_path, "background")
    os.makedirs(background_path, exist_ok=True)
    # Create the background object
    background_id = str(uuid.uuid4())
    background = DscaperBackground(
        library=properties.library,
        label=properties.label,
        source_file=properties.source_file,
        source_time=properties.source_time,
        id=background_id
    )
    # Save the background to a JSON file
    background_file = os.path.join(background_path, f"{background_id}.json")
    with open(background_file, "w") as f:
        f.write(background.model_dump_json())
    # Return a response indicating success
    return background


def add_event(name: str, properties: DscaperEvent):
    """Add an event to the timeline.
    
    :param name: The name of the timeline.
    :param properties: Properties for the event.
    :return: A DscaperEvent object containing the added event's metadata.
    Exceptions:
        - 404: If the timeline does not exist.
    """
    timeline_path = os.path.join(timeline_basedir, name)
    timeline_config = os.path.join(timeline_path, "timeline.json")
    # Check if the timeline exists
    if not os.path.exists(timeline_config):
        return Response(status_code=status.HTTP_404_NOT_FOUND, content=f"Timeline '{name}' does not exist.")
    # Create the events directory if it does not exist
    events_path = os.path.join(timeline_path, "events")
    os.makedirs(events_path, exist_ok=True)
    # Create the event object
    event_id = str(uuid.uuid4())
    event = DscaperEvent(
        library=properties.library,
        label=properties.label,
        source_file=properties.source_file,
        source_time=properties.source_time,
        event_time=properties.event_time,
        event_duration=properties.event_duration,
        snr=properties.snr,
        pitch_shift=properties.pitch_shift,
        time_stretch=properties.time_stretch,
        event_type=properties.event_type,
        id=event_id
    )
    # Save the event to a JSON file
    event_file = os.path.join(events_path, f"{event_id}.json")
    with open(event_file, "w") as f:
        f.write(event.model_dump_json())
    # Return a response indicating success
    return event