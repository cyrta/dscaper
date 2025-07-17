from scaper.dscaper_datatypes import *
import scaper
from typing import Annotated, Union
from fastapi import File,  status
import uuid
import os
import time
import soundfile
import json
import zipfile
import io


DSCAPER_DEFAULT_BASE_PATH = os.path.join(os.getcwd(), "data")


class Dscaper:
    """
    Dscaper offers an alternavie api to the Scaper library.
    """

    def __init__(self, dscaper_base_path: str | None = None):
        """
        Initialize the Dscaper with a base path for the libraries and timelines.
        :param dscaper_base_path: The base path for the libraries and timelines. If None, uses the default path.
        :raises FileNotFoundError: If the base path does not exist.
        """
        self.dscaper_base_path = dscaper_base_path if dscaper_base_path else DSCAPER_DEFAULT_BASE_PATH
        if not os.path.exists(self.dscaper_base_path):
            # retur error if the base path does not exist
            raise FileNotFoundError(f"Error. The specified library base path does not exist: {self.dscaper_base_path}")
        self.timeline_basedir = os.path.join(self.dscaper_base_path, "timelines")
        if not os.path.exists(self.timeline_basedir):
            os.makedirs(self.timeline_basedir)
        self.library_basedir = os.path.join(self.dscaper_base_path, "libraries")
        if not os.path.exists(self.library_basedir):
            os.makedirs(self.library_basedir)
    

    def get_dscaper_base_path(self) -> str:        
        """
        Returns the base path for the libraries.
        :return: The base path for the libraries.
        """        
        return self.dscaper_base_path
    

    def store_audio(self, file: Union[Annotated[bytes, File()], str], metadata: DscaperAudio, update: bool = False) -> DscaperJsonResponse:
        """
        Store audio file and its metadata.
        
        :param file: The audio file to be stored or a file path.
        :param metadata: Metadata for the audio file.
        :param update: If True, update the existing file, otherwise return an error if the file already exists.
        :return: An DscaperAudio object containing the stored audio's metadata.
        Exceptions:
            - 404: If the audio file does not exist.
            - 400: If the audio file is empty or invalid.
            - 400: If the file already exists and update is False.
            - 404: If the file does not exist and update is True.
        """
        m = metadata
        # if file is a path, read the file
        if isinstance(file, str):
            if not os.path.exists(file):
                return DscaperJsonResponse(status="error", status_code=status.HTTP_404_NOT_FOUND, content=json.dumps({"description": "File not found"}))
            with open(file, "rb") as f:
                file = f.read()
        # check if file is empty
        if len(file) == 0:
            return DscaperJsonResponse(status="error",status_code=status.HTTP_400_BAD_REQUEST,content=json.dumps({"description": "File is empty"}))
        # filename and path
        file_path = os.path.join(self.library_basedir, m.library, m.label)
        audio_destination = os.path.join(file_path, m.filename)
        base, ext = os.path.splitext(m.filename)
        metadata_destination = os.path.join(file_path, base + ".json")
        # check if the file already exists
        if os.path.exists(audio_destination) and not update:
            return DscaperJsonResponse(status="error", status_code=status.HTTP_400_BAD_REQUEST, content=json.dumps({"description": "File already exists. Use PUT to update it."}))
        elif not os.path.exists(audio_destination) and update:
            return DscaperJsonResponse(status="error", status_code=status.HTTP_404_NOT_FOUND, content=json.dumps({"description": "File does not exist. Use POST to create it."}))
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
            return DscaperJsonResponse(status="error", status_code=status.HTTP_400_BAD_REQUEST, content=json.dumps({"description": f"Invalid audio file: {str(e)}"}))
        # create the metadata object
        file_id = str(uuid.uuid4())
        timestamp = int(time.time())
        metadata_obj = DscaperAudio(id=file_id, library=m.library, label=m.label, filename=m.filename,  
                                sandbox=m.sandbox, timestamp=timestamp, duration=duration)
        # save the metadata to the audio metadata path
        with open(metadata_destination, "w") as f:
            f.write(metadata_obj.model_dump_json())
        # return the metadata object
        return DscaperJsonResponse(status_code=status.HTTP_200_OK, content=metadata_obj.model_dump_json())


    def read_audio(self, library: str, label: str, filename: str) -> DscaperApiResponse:
        """
        Read audio file (metadata or audio)
        
        :param library: The library of the audio file.
        :param label: The label of the audio file.
        :param filename: The name of the audio file.
        :return: An DscaperAudio object containing the audio's metadata or the audio file itself.
        Exceptions:
            - 404: If the audio file does not exist.
            - 400: If the audio file format is unsupported.
        """
        file = os.path.join(self.library_basedir, library, label, filename)
        if not os.path.exists(file):
            return DscaperApiResponse(status="error", status_code=status.HTTP_404_NOT_FOUND, content="Audio file not found")
        base, ext = os.path.splitext(filename)
        # requesting metadata
        if ext.lower() == ".json":
            with open(file, "r") as f:
                metadata_json = f.read()
            return DscaperApiResponse(status="success", status_code=status.HTTP_200_OK, content=DscaperAudio.model_validate_json(metadata_json).model_dump_json(), media_type="application/json")
        # requesting audio file
        elif ext.lower() in [".wav", ".mp3", ".flac", ".ogg"]:
            with open(file, "rb") as f:
                audio_data = f.read()
            return DscaperApiResponse(status="success", status_code=status.HTTP_200_OK, content=audio_data, media_type="audio/" + ext[1:])
        else:
            return DscaperApiResponse(status="error", status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, content="Unsupported audio file format")
        

    def get_libraries(self) -> DscaperJsonResponse:
        """
        Get a list of all audio libraries.
        
        :return: A list of library names.
        """
        libraries = []
        for root, dirs, files in os.walk(self.library_basedir):
            if root == self.library_basedir:
                libraries.extend(dirs)
        return DscaperJsonResponse(content=json.dumps(libraries))


    def get_filenames(self, library: str, label: str) -> DscaperJsonResponse:
        """
        Get a list of all filenames in a specific audio label.
        
        :param library: The library to get filenames from.
        :param label: The label to get filenames from.
        :return: A list of filenames in the specified label.
        Exceptions:
            - 404: If the library or label does not exist.
        """
        library_path = os.path.join(self.library_basedir, library, label)
        if not os.path.exists(library_path):
            return DscaperJsonResponse(status="error", status_code=status.HTTP_404_NOT_FOUND, content=json.dumps({"description": "Library not found"}))
        
        filenames = []
        for file in os.listdir(library_path):
            if os.path.isfile(os.path.join(library_path, file)):
                filenames.append(file)
        return DscaperJsonResponse(content=json.dumps(filenames))


    def get_labels(self, library: str) -> DscaperJsonResponse:
        """
        Get a list of all labels in a specific audio library.
        
        :param library: The library to get labels from.
        :return: A list of label names in the specified library.
        """
        library_path = os.path.join(self.library_basedir, library)
        if not os.path.exists(library_path):
            return DscaperJsonResponse(status="error", status_code=status.HTTP_404_NOT_FOUND, content=json.dumps({"description": "Library not found"}))    
        labels = []
        for root, dirs, files in os.walk(library_path):
            if root == library_path:
                labels.extend(dirs)
        return DscaperJsonResponse(content=json.dumps(labels))


    def create_timeline(self, properties: DscaperTimeline) -> DscaperJsonResponse:
        """Create a new timeline.
        
        :param name: The name of the timeline.
        :param properties: Properties for the timeline.
        :return: A Timeline object containing the created timeline's metadata.
        Exceptions:
            - 400: If the timeline already exists.
        """
        p = properties
        timeline_path = os.path.join(self.timeline_basedir, p.name)
        timeline_config = os.path.join(timeline_path, "timeline.json")
        # Check if the timeline already exists
        if os.path.exists(timeline_config):
            return DscaperJsonResponse(status="error", status_code=status.HTTP_400_BAD_REQUEST, content=json.dumps({"description": f"Timeline '{p.name}' already exists."}))
        # Create the directory if it does not exist
        os.makedirs(timeline_path, exist_ok=True)
        # Create the Timeline object
        file_id = str(uuid.uuid4())
        timestamp = int(time.time())
        timeline = DscaperTimeline(
            id=file_id,
            name=p.name,
            duration=p.duration,
            description=p.description,
            sandbox=p.sandbox,
            timestamp=timestamp
        )
        # Save the timeline to a JSON file
        with open(timeline_config, "w") as f:
            f.write(timeline.model_dump_json())
        # Return the created timeline object
        return DscaperJsonResponse(status_code=status.HTTP_201_CREATED,content=timeline.model_dump_json())
        

    def add_background(self, name: str, properties: DscaperBackground) -> DscaperJsonResponse:
        """Add a background to the timeline.
        
        :param name: The name of the timeline.
        :param properties: Properties for the background.
        :return: A DscaperBackground object containing the added background's metadata.
        Exceptions:
            - 404: If the timeline does not exist.
        """
        timeline_path = os.path.join(self.timeline_basedir, name)
        timeline_config = os.path.join(timeline_path, "timeline.json")
        # Check if the timeline exists
        if not os.path.exists(timeline_config):
            return DscaperJsonResponse(status="error", status_code=status.HTTP_404_NOT_FOUND, content=json.dumps({"description": f"Timeline '{name}' does not exist."}))
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
        return DscaperJsonResponse(status_code=status.HTTP_201_CREATED, content=background.model_dump_json())


    def add_event(self, name: str, properties: DscaperEvent) -> DscaperJsonResponse:
        """Add an event to the timeline.
        
        :param name: The name of the timeline.
        :param properties: Properties for the event.
        :return: A DscaperEvent object containing the added event's metadata.
        Exceptions:
            - 404: If the timeline does not exist.
        """
        timeline_path = os.path.join(self.timeline_basedir, name)
        timeline_config = os.path.join(timeline_path, "timeline.json")
        # Check if the timeline exists
        if not os.path.exists(timeline_config):
            return DscaperJsonResponse(status="error", status_code=status.HTTP_404_NOT_FOUND, content=json.dumps({"description": f"Timeline '{name}' does not exist."}))
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
        return DscaperJsonResponse(status_code=status.HTTP_201_CREATED, content=event.model_dump_json())


    def generate_timeline(self, name: str, properties: DscaperGenerate) -> DscaperJsonResponse:
        """Generate the timeline.
        
        :param name: The name of the timeline.
        :param properties: Properties for the generation.
        :return: A response indicating the timeline was generated.
        Exceptions:
            - 404: If the timeline does not exist.
        """
        timeline_path = os.path.join(self.timeline_basedir, name)
        timeline_config = os.path.join(timeline_path, "timeline.json")
        # Check if the timeline exists
        if not os.path.exists(timeline_config):
            return DscaperJsonResponse(status="error", status_code=status.HTTP_404_NOT_FOUND, content=json.dumps({"description": f"Timeline '{name}' does not exist."}))
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
        sc.ref_db = properties.ref_db  # Set the reference dB level
        # add backgrounds
        for bg in os.listdir(os.path.join(timeline_path, "background")):
            # print(f"*** Processing background: {bg}")
            bg_file = os.path.join(timeline_path, "background", bg)
            if os.path.isfile(bg_file):
                with open(bg_file, "r") as f:
                    background = DscaperBackground.model_validate_json(f.read())
                sc.add_background(
                    label=self._get_distribution_tuple(background.label),
                    source_file=self._get_distribution_tuple(background.source_file),
                    source_time=self._get_distribution_tuple(background.source_time),
                    library=os.path.join(self.library_basedir, background.library) if background.library else None
                )
        # add events
        for event in os.listdir(os.path.join(timeline_path, "events")):
            event_file = os.path.join(timeline_path, "events", event)
            if os.path.isfile(event_file):
                with open(event_file, "r") as f:
                    event_data = DscaperEvent.model_validate_json(f.read())
                if not event_data.event_duration:
                    # If event_duration is not set, use duration of the audio file or default to 5 seconds
                    event_data.event_duration = ['const', '5']
                    if event_data.source_file and event_data.source_file[0] == 'const':
                        source_file_path = os.path.join(self.library_basedir, event_data.library, event_data.label[1], event_data.source_file[1])
                        if os.path.isfile(source_file_path):
                            duration = soundfile.info(source_file_path).duration
                            event_data.event_duration = ['const', str(duration)]
                sc.add_event(
                    label=self._get_distribution_tuple(event_data.label),
                    source_file=self._get_distribution_tuple(event_data.source_file),
                    source_time=self._get_distribution_tuple(event_data.source_time),
                    event_time=self._get_distribution_tuple(event_data.event_time),
                    event_duration=self._get_distribution_tuple(event_data.event_duration),
                    snr=self._get_distribution_tuple(event_data.snr),
                    pitch_shift=self._get_distribution_tuple(event_data.pitch_shift) if event_data.pitch_shift else None,
                    time_stretch=self._get_distribution_tuple(event_data.time_stretch) if event_data.time_stretch else None,
                    event_type=event_data.event_type,
                    library=os.path.join(self.library_basedir, event_data.library) if event_data.library else None
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
        return DscaperJsonResponse(
            status_code=status.HTTP_201_CREATED,
            content=properties.model_dump_json(),
        )


    def list_timelines(self) -> DscaperJsonResponse:
        """List all timelines.

        :return: A list of timelines.
        """
        timelines = DscaperTimelines()
        for root, dirs, files in os.walk(self.timeline_basedir):
            if root == self.timeline_basedir:
                for dir_name in dirs:
                    timeline_path = os.path.join(root, dir_name, "timeline.json")
                    if os.path.exists(timeline_path):
                        with open(timeline_path, "r") as f:
                            timeline = DscaperTimeline.model_validate_json(f.read())
                            timelines.timelines.append(timeline)
        return DscaperJsonResponse(content=timelines.model_dump_json())


    def list_backgrounds(self, timeline_name: str) -> DscaperJsonResponse:
        """List all backgrounds in the timeline.
        
        :param timeline_name: The name of the timeline.
        :return: A list of backgrounds.
        Exceptions:
            - 404: If the timeline does not exist.
        """
        timeline_path = os.path.join(self.timeline_basedir, timeline_name)
        background_path = os.path.join(timeline_path, "background")
        # Check if the timeline exists
        if not os.path.exists(background_path):
            return DscaperJsonResponse(
                status="error",
                status_code=status.HTTP_404_NOT_FOUND,
                content=json.dumps({"description": f"Timeline '{timeline_name}' does not exist."})
            )
        backgrounds = DscaperBackgrounds()
        for bg_file in os.listdir(background_path):
            bg_file_path = os.path.join(background_path, bg_file)
            if os.path.isfile(bg_file_path):
                with open(bg_file_path, "r") as f:
                    background = DscaperBackground.model_validate_json(f.read())
                    backgrounds.backgrounds.append(background)
        return DscaperJsonResponse(
            content=backgrounds.model_dump_json(),
        )


    def list_events(self, timeline_name: str) -> DscaperJsonResponse:
        """List all events in the timeline.
        
        :param timeline_name: The name of the timeline.
        :return: A list of events.
        Exceptions:
            - 404: If the timeline does not exist.
        """
        timeline_path = os.path.join(self.timeline_basedir, timeline_name)
        events_path = os.path.join(timeline_path, "events")
        # Check if the timeline exists
        if not os.path.exists(events_path):
            return DscaperJsonResponse(
                status="error",
                status_code=status.HTTP_404_NOT_FOUND,
                content=json.dumps({"description": f"Timeline '{timeline_name}' does not exist."})
            )
        events = DscaperEvents()
        for event_file in os.listdir(events_path):
            event_file_path = os.path.join(events_path, event_file)
            if os.path.isfile(event_file_path):
                with open(event_file_path, "r") as f:
                    event = DscaperEvent.model_validate_json(f.read())
                    events.events.append(event)
        return DscaperJsonResponse(content=events.model_dump_json())


    def get_generated_timelines(self, timeline_name: str) -> DscaperJsonResponse:
        """Get the generated timeline.
        
        :param timeline_name: The name of the timeline.
        :return: The generated timeline.
        Exceptions:
            - 404: If the timeline does not exist.
        """
        timeline_path = os.path.join(self.timeline_basedir, timeline_name)
        generate_path = os.path.join(timeline_path, "generate")
        # Check if the timeline exists
        if not os.path.exists(generate_path):
            return DscaperJsonResponse(
                status="error",
                status_code=status.HTTP_404_NOT_FOUND,
                content=json.dumps({"description": f"Timeline '{timeline_name}' does not exist."})
            )
        # Read properties of all generated timelines
        generated_timelines = DscaperGenerations()
        for generate_dir in os.listdir(generate_path):
            generate_dir_path = os.path.join(generate_path, generate_dir)
            if os.path.isdir(generate_dir_path):
                properties_file = os.path.join(generate_dir_path, "generate.json")
                if os.path.exists(properties_file):
                    with open(properties_file, "r") as f:
                        properties = DscaperGenerate.model_validate_json(f.read())
                        generated_timelines.generations.append(properties)
        # Return the list of generated timelines
        return DscaperJsonResponse(content=generated_timelines.model_dump_json())


    def get_generated_timeline_by_id(self, timeline_name: str, generate_id: str) -> DscaperJsonResponse:
        """Get a specific generated timeline by ID.
        
        :param timeline_name: The name of the timeline.
        :param generate_id: The ID of the generated timeline.
        :return: The generated timeline properties.
        Exceptions:
            - 404: If the timeline or generated timeline does not exist.
        """
        timeline_path = os.path.join(self.timeline_basedir, timeline_name)
        generate_dir = os.path.join(timeline_path, "generate", generate_id)
        # Check if the timeline exists
        if not os.path.exists(generate_dir):
            return DscaperJsonResponse(
                status="error",
                status_code=status.HTTP_404_NOT_FOUND,
                content=json.dumps({"description": f"Timeline '{timeline_name}' or generated timeline with ID '{generate_id}' does not exist."})
            )
        properties_file = os.path.join(generate_dir, "generate.json")
        if not os.path.exists(properties_file):
            return DscaperJsonResponse(
                status="error",
                status_code=status.HTTP_404_NOT_FOUND,
                content=json.dumps({"description": f"Generated timeline with ID '{generate_id}' does not exist."})
            )
        with open(properties_file, "r") as f:
            properties = DscaperGenerate.model_validate_json(f.read())
        return DscaperJsonResponse(content=properties.model_dump_json())


    def get_generated_file(self, timeline_name: str, generate_id: str, file_name: str) -> DscaperApiResponse:
        """Get a specific generated file from the timeline.
        
        :param timeline_name: The name of the timeline.
        :param generate_id: The ID of the generated timeline.
        :param file_name: The name of the generated file.
        :return: The generated file content or an error response if not found.
        Exceptions:
            - 404: If the timeline or generated file does not exist.
        """
        timeline_path = os.path.join(self.timeline_basedir, timeline_name)
        generate_dir = os.path.join(timeline_path, "generate", generate_id)
        # Check if the timeline exists
        if not os.path.exists(generate_dir):
            return DscaperApiResponse(
                status="error",
                status_code=status.HTTP_404_NOT_FOUND,
                content=f"Timeline '{timeline_name}' or generated timeline with ID '{generate_id}' does not exist."
            )
        file_path = os.path.join(generate_dir, file_name)
        if not os.path.exists(file_path):
            return DscaperApiResponse(
                status="error",
                status_code=status.HTTP_404_NOT_FOUND,
                content=f"Generated file '{file_name}' does not exist in timeline '{timeline_name}' with ID '{generate_id}'."
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
        
    def get_generated_files(self, timeline_name: str, generate_id: str) -> DscaperApiResponse:
        """Get all generated files from the timeline.
        
        :param timeline_name: The name of the timeline.
        :param generate_id: The ID of the generated timeline.
        :return: A list of generated files or an error response if not found.
        Exceptions:
            - 404: If the timeline or generated files do not exist.
        """
        timeline_path = os.path.join(self.timeline_basedir, timeline_name)
        generate_dir = os.path.join(timeline_path, "generate", generate_id)
        # Check if the timeline exists
        if not os.path.exists(generate_dir):
            return DscaperApiResponse(
                status="error",
                status_code=status.HTTP_404_NOT_FOUND,
                content=f"Timeline '{timeline_name}' or generated timeline with ID '{generate_id}' does not exist."
            )
        # compress the folder into a zip file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(generate_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, generate_dir))
        # Return the zip file as a response
        zip_buffer.seek(0)
        zip_data = zip_buffer.read()
        return DscaperApiResponse(
            status="success",
            status_code=status.HTTP_200_OK,
            content=zip_data,
            media_type="application/zip"
        )


    # Helper functions to convert distributions
    # to tuples for scaper compatibility

    def _get_distribution_tuple(self, distribution):
        """Convert a distribution list to a tuple."""
        # print(f"*** Processing distribution: {distribution}")
        if not isinstance(distribution, list):
            raise ValueError("Distribution must be a list or string.")
        dist_type = distribution[0]
        if dist_type == 'const':
            if len(distribution) != 2:
                raise ValueError("Constant distribution must have exactly one value.")
            value = distribution[1]
            return_tuple = (dist_type, value)
            # check if value is a number or a string
            if isinstance(value, str):
                if value.isnumeric() or self._isfloat(value):
                    # print("its a number", value)
                    return_tuple = (dist_type, float(value))
                else:
                    # print("its a string", value)
                    return_tuple = (dist_type, value)
            else:
                raise ValueError("Constant distribution value must be a number or a string.")
            # print(f"*** Returning constant distribution tuple: {return_tuple}")
            return return_tuple
        elif dist_type == 'choose':
            if len(distribution) != 2:
                raise ValueError("Choose distribution must have exactly one list of values.")
            return (dist_type, self._string_to_list(distribution[1]))
        elif dist_type == 'choose_weighted':    
            if len(distribution) != 3:
                raise ValueError("Choose weighted distribution must have exactly one list of values and one list of weights.")
            return (dist_type, self._string_to_list(distribution[1]), self._string_to_list(distribution[2]))
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
        
    def _string_to_list(self, string):
        """Convert a string to a list."""
        if not isinstance(string, str):
            raise ValueError("Input must be a string.")
        # remove brackets
        string = string.strip().strip('[]')
        output_list = [s.strip() for s in string.split(',') if s.strip()]
        # print(f"*** Converting string to list: {string} to {output_list}")
        return output_list
    
    def _isfloat(self, string):
        if not isinstance(string, str):
            return False
        try:
            float(string)
        except ValueError:
            return False
        return True
