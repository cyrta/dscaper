from web.services.web_models import TimelineCreateDTO, DscaperTimeline, DscaperBackground, DscaperEvent, DscaperGenerate, DscaperApiResponse
from fastapi import APIRouter, Response, status
import os
import uuid
import time
import scaper

timeline_basedir = os.path.join(os.getcwd(), "data", "timeline")
library_basedir = os.path.join(os.getcwd(), "data", "audio")


def create_timeline(name: str, properties: TimelineCreateDTO) -> DscaperApiResponse:
    """Create a new timeline.
    
    :param name: The name of the timeline.
    :param properties: Properties for the timeline.
    :return: A Timeline object containing the created timeline's metadata.
    """
    timeline_path = os.path.join(timeline_basedir, name)
    timeline_config = os.path.join(timeline_path, "timeline.json")
    # Check if the timeline already exists
    if os.path.exists(timeline_config):
        return DscaperApiResponse(status="error", status_code=status.HTTP_400_BAD_REQUEST, content=f"Timeline '{name}' already exists.")
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
        description=p.description,
        sandbox=p.sandbox,
        timestamp=timestamp
    )
    # Save the timeline to a JSON file
    with open(timeline_config, "w") as f:
        f.write(timeline.model_dump_json())
    # Return the created timeline object
    return DscaperApiResponse(status="success",status_code=status.HTTP_201_CREATED,content=timeline.model_dump_json(),media_type="application/json")
    

def add_background(name: str, properties: DscaperBackground) -> DscaperApiResponse:
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
        return DscaperApiResponse(status="error", status_code=status.HTTP_404_NOT_FOUND, content=f"Timeline '{name}' does not exist.")
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
    return DscaperApiResponse(status="success", status_code=status.HTTP_201_CREATED, content=background.model_dump_json(), media_type="application/json")


def add_event(name: str, properties: DscaperEvent) -> DscaperApiResponse:
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
        return DscaperApiResponse(status="error", status_code=status.HTTP_404_NOT_FOUND, content=f"Timeline '{name}' does not exist.")
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
    return DscaperApiResponse(status="success", status_code=status.HTTP_201_CREATED, content=event.model_dump_json(), media_type="application/json")


def generate_timeline(name: str, properties: DscaperGenerate) -> DscaperApiResponse:
    """Generate the timeline.
    
    :param name: The name of the timeline.
    :param properties: Properties for the generation.
    :return: A response indicating the timeline was generated.
    Exceptions:
        - 404: If the timeline does not exist.
    """
    timeline_path = os.path.join(timeline_basedir, name)
    timeline_config = os.path.join(timeline_path, "timeline.json")
    # Check if the timeline exists
    if not os.path.exists(timeline_config):
        return DscaperApiResponse(status="error", status_code=status.HTTP_404_NOT_FOUND, content=f"Timeline '{name}' does not exist.")
    # Create the generate directory if it does not exist
    generate_base = os.path.join(timeline_path, "generate")
    os.makedirs(generate_base, exist_ok=True)
    # Load the timeline configuration
    with open(timeline_config, "r") as f:
        timeline = DscaperTimeline.model_validate_json(f.read())
    # add properties to the generation
    generate_id = str(uuid.uuid4())
    generate_dir = os.path.join(generate_base, generate_id)
    os.makedirs(generate_dir, exist_ok=True)
    properties.id = generate_id
    properties.timestamp = int(time.time())
    # Use scaper to generate the timeline
    sc = scaper.Scaper(
        duration=timeline.duration,
        fg_path=None,  # fg_path is not used in this context
        bg_path=None,  # bg_path is not used in this context
        random_state=properties.seed
    )
    # add backgrounds
    for bg in os.listdir(os.path.join(timeline_path, "background")):
        print(f"*** Processing background: {bg}")
        bg_file = os.path.join(timeline_path, "background", bg)
        if os.path.isfile(bg_file):
            with open(bg_file, "r") as f:
                background = DscaperBackground.model_validate_json(f.read())
            sc.add_background(
                label=get_distribution_tuple(background.label),
                source_file=get_distribution_tuple(background.source_file),
                source_time=get_distribution_tuple(background.source_time),
                library=os.path.join(library_basedir, background.library) if background.library else None
            )
    # add events
    for event in os.listdir(os.path.join(timeline_path, "events")):
        print(f"*** Processing event: {event}")
        event_file = os.path.join(timeline_path, "events", event)
        if os.path.isfile(event_file):
            with open(event_file, "r") as f:
                event_data = DscaperEvent.model_validate_json(f.read())
            sc.add_event(
                label=get_distribution_tuple(event_data.label),
                source_file=get_distribution_tuple(event_data.source_file),
                source_time=get_distribution_tuple(event_data.source_time),
                event_time=get_distribution_tuple(event_data.event_time),
                event_duration=get_distribution_tuple(event_data.event_duration),
                snr=get_distribution_tuple(event_data.snr),
                pitch_shift=get_distribution_tuple(event_data.pitch_shift) if event_data.pitch_shift else None,
                time_stretch=get_distribution_tuple(event_data.time_stretch) if event_data.time_stretch else None,
                event_type=event_data.event_type,
                library=os.path.join(library_basedir, event_data.library) if event_data.library else None
            )
    # Generate the timeline
    audiofile = os.path.join(generate_dir, "soundscape.wav")
    jamsfile = os.path.join(generate_dir, "soundscape.jams")
    txtfile = os.path.join(generate_dir, "soundscape.txt")
    sc.generate(
        audio_path=audiofile,
        jams_path=jamsfile,
        allow_repeated_label=True,
        allow_repeated_source=True,
        reverb=properties.reverb,
        disable_sox_warnings=True,
        no_audio=False,
        txt_path=txtfile,
        save_isolated_events=properties.save_isolated_events,
        save_isolated_eventtypes=properties.save_isolated_eventtypes
    )
    # add the generated files in the properties
    properties.generated_files = []
    for file in os.listdir(generate_dir):
        if file.endswith(('.wav', '.jams', '.txt')):
            properties.generated_files.append(file)
    # Save the properties to a JSON file
    properties_file = os.path.join(generate_dir, "generate.json")
    with open(properties_file, "w") as f:
        f.write(properties.model_dump_json())
    return DscaperApiResponse(
        status="success",
        status_code=status.HTTP_201_CREATED,
        content=properties.model_dump_json(),
        media_type="application/json"
    )


def list_timelines() -> DscaperApiResponse:
    """List all timelines.

    :return: A list of timelines.
    """
    timelines = []
    for root, dirs, files in os.walk(timeline_basedir):
        if root == timeline_basedir:
            for dir_name in dirs:
                timeline_path = os.path.join(root, dir_name, "timeline.json")
                if os.path.exists(timeline_path):
                    with open(timeline_path, "r") as f:
                        timeline = DscaperTimeline.model_validate_json(f.read())
                        timelines.append(timeline)
    return DscaperApiResponse(
        status="success",
        status_code=status.HTTP_200_OK,
        content=str([timeline.model_dump_json() for timeline in timelines]),
        media_type="application/json"
    )


def list_backgrounds(name: str) -> DscaperApiResponse:
    """List all backgrounds in the timeline.
    
    :param name: The name of the timeline.
    :return: A list of backgrounds.
    Exceptions:
        - 404: If the timeline does not exist.
    """
    timeline_path = os.path.join(timeline_basedir, name)
    background_path = os.path.join(timeline_path, "background")
    # Check if the timeline exists
    if not os.path.exists(background_path):
        return DscaperApiResponse(
            status="error",
            status_code=status.HTTP_404_NOT_FOUND,
            content=f"Timeline '{name}' does not exist."
        )
    backgrounds = []
    for bg_file in os.listdir(background_path):
        bg_file_path = os.path.join(background_path, bg_file)
        if os.path.isfile(bg_file_path):
            with open(bg_file_path, "r") as f:
                background = DscaperBackground.model_validate_json(f.read())
                backgrounds.append(background)
    return DscaperApiResponse(
        status="success",
        status_code=status.HTTP_200_OK,
        content=str([bg.model_dump_json() for bg in backgrounds]),
        media_type="application/json"
    )


def list_events(name: str) -> DscaperApiResponse:
    """List all events in the timeline.
    
    :param name: The name of the timeline.
    :return: A list of events.
    Exceptions:
        - 404: If the timeline does not exist.
    """
    timeline_path = os.path.join(timeline_basedir, name)
    events_path = os.path.join(timeline_path, "events")
    # Check if the timeline exists
    if not os.path.exists(events_path):
        return DscaperApiResponse(
            status="error",
            status_code=status.HTTP_404_NOT_FOUND,
            content=f"Timeline '{name}' does not exist."
        )
    events = []
    for event_file in os.listdir(events_path):
        event_file_path = os.path.join(events_path, event_file)
        if os.path.isfile(event_file_path):
            with open(event_file_path, "r") as f:
                event = DscaperEvent.model_validate_json(f.read())
                events.append(event)
    return DscaperApiResponse(
        status="success",
        status_code=status.HTTP_200_OK,
        content=str([event.model_dump_json() for event in events]),
        media_type="application/json"
    )


def get_generated_timelines(name: str) -> DscaperApiResponse:
    """Get the generated timeline.
    
    :param name: The name of the timeline.
    :return: The generated timeline.
    Exceptions:
        - 404: If the timeline does not exist.
    """
    timeline_path = os.path.join(timeline_basedir, name)
    generate_path = os.path.join(timeline_path, "generate")
    # Check if the timeline exists
    if not os.path.exists(generate_path):
        return DscaperApiResponse(
            status="error",
            status_code=status.HTTP_404_NOT_FOUND,
            content=f"Timeline '{name}' does not exist."
        )
    # Read properties of all generated timelines
    generated_timelines = []
    for generate_dir in os.listdir(generate_path):
        generate_dir_path = os.path.join(generate_path, generate_dir)
        if os.path.isdir(generate_dir_path):
            properties_file = os.path.join(generate_dir_path, "generate.json")
            if os.path.exists(properties_file):
                with open(properties_file, "r") as f:
                    properties = DscaperGenerate.model_validate_json(f.read())
                    generated_timelines.append(properties)
    # Return the list of generated timelines
    return DscaperApiResponse(
        status="success",
        status_code=status.HTTP_200_OK,
        content=str([timeline.model_dump_json() for timeline in generated_timelines]),
        media_type="application/json"
    )


def get_generated_timeline_by_id(name: str, generate_id: str) -> DscaperApiResponse:
    """Get a specific generated timeline by ID.
    
    :param name: The name of the timeline.
    :param generate_id: The ID of the generated timeline.
    :return: The generated timeline properties.
    Exceptions:
        - 404: If the timeline or generated timeline does not exist.
    """
    timeline_path = os.path.join(timeline_basedir, name)
    generate_dir = os.path.join(timeline_path, "generate", generate_id)
    # Check if the timeline exists
    if not os.path.exists(generate_dir):
        return DscaperApiResponse(
            status="error",
            status_code=status.HTTP_404_NOT_FOUND,
            content=f"Timeline '{name}' or generated timeline with ID '{generate_id}' does not exist."
        )
    properties_file = os.path.join(generate_dir, "generate.json")
    if not os.path.exists(properties_file):
        return DscaperApiResponse(
            status="error",
            status_code=status.HTTP_404_NOT_FOUND,
            content=f"Generated timeline with ID '{generate_id}' does not exist."
        )
    with open(properties_file, "r") as f:
        properties = DscaperGenerate.model_validate_json(f.read())
    return DscaperApiResponse(
        status="success",
        status_code=status.HTTP_200_OK,
        content=properties.model_dump_json(),
        media_type="application/json"
    )


def get_generated_file(name: str, generate_id: str, file_name: str) -> DscaperApiResponse:
    """Get a specific generated file from the timeline.
    
    :param name: The name of the timeline.
    :param generate_id: The ID of the generated timeline.
    :param file_name: The name of the generated file.
    :return: The generated file content or an error response if not found.
    Exceptions:
        - 404: If the timeline or generated file does not exist.
    """
    timeline_path = os.path.join(timeline_basedir, name)
    generate_dir = os.path.join(timeline_path, "generate", generate_id)
    # Check if the timeline exists
    if not os.path.exists(generate_dir):
        return DscaperApiResponse(
            status="error",
            status_code=status.HTTP_404_NOT_FOUND,
            content=f"Timeline '{name}' or generated timeline with ID '{generate_id}' does not exist."
        )
    file_path = os.path.join(generate_dir, file_name)
    if not os.path.exists(file_path):
        return DscaperApiResponse(
            status="error",
            status_code=status.HTTP_404_NOT_FOUND,
            content=f"Generated file '{file_name}' does not exist in timeline '{name}' with ID '{generate_id}'."
        )
    # requesting metadata
    base, ext = os.path.splitext(file_name)
    if ext.lower() == ".json" or ext.lower() == ".jams":
        # If the file is a JSON or TXT file, read it as metadata
        with open(file_path, "r") as f:
            data_json = f.read()
        return DscaperApiResponse(
            status="success",
            status_code=status.HTTP_200_OK,
            content=data_json,
            media_type="application/json"
        )
    # requesting audio file
    elif ext.lower() in [".wav", ".mp3", ".flac", ".ogg"]:
        with open(file_path, "rb") as f:
            audio_data = f.read()
        return DscaperApiResponse(
            status="success",
            status_code=status.HTTP_200_OK,
            content=audio_data,
            media_type="audio/" + ext[1:]
        )
    elif ext.lower() == ".txt":
        # If the file is a TXT file, read it as text content
        with open(file_path, "r") as f:
            text_content = f.read()
        return DscaperApiResponse(
            status="success",
            status_code=status.HTTP_200_OK,
            content=text_content,
            media_type="text/plain"
        )
    # Return bad request for unsupported formats
    else:
        return DscaperApiResponse(
            status="error",
            status_code=status.HTTP_400_BAD_REQUEST,
            content="Unsupported file format"
        )



# Helper functions to convert distributions
# to tuples for scaper compatibility

def get_distribution_tuple(distribution):
    """Convert a distribution list to a tuple."""
    print(f"*** Processing distribution: {distribution}")
    if not isinstance(distribution, list):
        raise ValueError("Distribution must be a list or string.")
        return None
    dist_type = distribution[0]
    if dist_type == 'const':
        if len(distribution) != 2:
            raise ValueError("Constant distribution must have exactly one value.")
        value = distribution[1]
        return_tuple = (dist_type, value)
        # check if value is a number or a string
        if isinstance(value, str):
            if value.isnumeric():
                return_tuple = (dist_type, float(value))
            else:
                return_tuple = (dist_type, value)
        else:
            raise ValueError("Constant distribution value must be a number or a string.")
        print(f"*** Returning constant distribution tuple: {return_tuple}")
        return return_tuple
    elif dist_type == 'choose':
        if len(distribution) != 2:
            raise ValueError("Choose distribution must have exactly one list of values.")
        return (dist_type, string_to_list(distribution[1]))
    elif dist_type == 'choose_weighted':    
        if len(distribution) != 3:
            raise ValueError("Choose weighted distribution must have exactly one list of values and one list of weights.")
        return (dist_type, string_to_list(distribution[1]), string_to_list(distribution[2]))
    elif dist_type == 'uniform':
        if len(distribution) != 3:
            raise ValueError("Uniform distribution must have exactly two values (min, max).")
        return (dist_type, float(distribution[1]), float(distribution[2]))
    elif dist_type == 'truncnorm':
        if len(distribution) != 5:
            raise ValueError("Truncated normal distribution must have exactly four values (mean, std, a, b).")
        return (dist_type, float(distribution[1]), float(distribution[2]), float(distribution[3]), float(distribution[4]))
    elif dist_type == 'normal':
        if len(distribution) != 3:
            raise ValueError("Normal distribution must have exactly two values (mean, std).")
        return (dist_type, float(distribution[1]), float(distribution[2]))
    else:
        raise ValueError("Invalid distribution format. Must be a list or string.")
    
def string_to_list(string):
    """Convert a string to a list."""
    if not isinstance(string, str):
        raise ValueError("Input must be a string.")
    # remove brackets
    string = string.strip().strip('[]')
    output_list = [s.strip() for s in string.split(',') if s.strip()]
    print(f"*** Converting string to list: {string} to {output_list}")
    return output_list