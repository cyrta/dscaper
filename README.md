# dScaper

![dScaper logo](/docs/dScaper-logo.png)

***A [Scaper](https://github.com/justinsalamon/scaper) fork optimized for audio generation pipelines.*** 

dScaper was developped during [JSALT25](https://jsalt2025.fit.vut.cz/) Workshop by David Grünert. dScaper offers an 
alternative API for accessing Scaper that is optimized for the usage in pipelines. Please refer to 
[Scaper documentation](http://scaper.readthedocs.io/) for details of the original Scaper API.

## Table of Contents

- [Architecture and key features](#architecture-and-key-features)
- [Installation](#installation)
- [Python API](#python-api)
  - [Adding audio files to the library](#adding-audio-files-to-the-library)
  - [Assemble timelines](#assemble-timelines)
    - [Adding background sounds](#adding-background-sounds)
    - [Adding events](#adding-events)
  - [Generating timelines](#generating-timelines)
  - [dScaper class methods](#dscaper-class-methods)
- [Web API](#web-api)
  - [Audio API](#audio-api)
  - [Timeline API](#timeline-api)
- [Distribution lists](#distribution-lists)
- [Folder structure](#folder-structure)
- [Misc](#misc)


## Architecture and key features

dScaper can eighter be use as python module or as separate server. In both variants, dScaper not only handles timeline generation, but it also stores and manages audio files.

![architecture overview](docs/dscaper_architecture.drawio.svg)

The main features of dScaper are:
- **Audio library management**: dScaper allows you to store and manage audio files in a structured way. Audio files are organized into libraries and labels, making it easy to retrieve and use them in multiple timelines.
- **Timeline management**: dScaper allows you to create and edit timelines, which define the structure of the generated audio including background sounds and events. dScaper supports the same distributions for sampling as the original Scaper library.
- **Audio generation**: dScaper can generate multiple version of a timeline. It stores the generated audio files along with their metadata making it easy to retrieve and compare them later.
- **Event positions**: dScaper supports event positions, allowing you to categorize events in the timeline. This is useful for generating multiple audio files for different event positions, e.g. to apply different room acoustics to different speakers and sound sources.
- **Speaker and text metadata**: dScaper allows you to add speaker and text metadata to events. This is useful for generating audio files with speaker and text annotations.
- **Web API and Python API**: dScaper provides a RESTful Web API and a Python API. The web API allows to use dScaper as a standalone server simplifying integration and scaling of pipelines.

## Installation

### Non-python dependencies
Scaper has one non-python dependency:
- FFmpeg: https://ffmpeg.org/

If you are installing Scaper on Windows, you will also need:
- SoX: http://sox.sourceforge.net/

On Linux/macOS SoX is replaced by [SoxBindings](https://github.com/pseeth/soxbindings) which is significantly faster, giving better runtime performance in Scaper. On these platforms SoxBindings is installed automatically when calling `pip install scaper` (see below).


#### macOS
On macOS FFmpeg can be installed using [homebrew](https://brew.sh/):

```
brew install ffmpeg
```

#### Linux
On linux you can use your distribution's package manager, e.g. on Ubuntu (15.04 "Vivid Vervet" or newer):

```
sudo apt-get install ffmpeg
```

#### Windows
On windows you can use the provided installation binaries:
- SoX: https://sourceforge.net/projects/sox/files/sox/
- FFmpeg: https://ffmpeg.org/download.html#build-windows

### Installing Scaper

To install the latest version of scaper from source, clone or pull the lastest version:

```
git clone https://github.com/cyrta/dscaper
```

Then create an environment and install the package from requirements.txt:

```
cd scaper
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```
## Python API
You can use dScaper as a Python module. The main class is `Dscaper`, which provides methods for creating timelines, adding audio files, and generating audio. dScaper needs a folder to store audio files, metadata and timelines. You can specify this folder using the `dscaper_base_path` parameter when creating an instance of `Dscaper`. If you do not specify it, dScaper will use the default path `./data`.

```python
import scaper

dsc = scaper.Dscaper(dscaper_base_path="/path/to/dscaper/data")
```

dScaper will create two subfolders `libraries` and `timelines` in the specified path if they do not already exist. 

```/path/to/dscaper/data/
├── libraries
│   └── [library_data...]
└── timelines
    └── [timeline_data...]
```
The librarys folder is used to store the input audio files and their metadata. The timeline folder contains the definition and the resulting audio of the generated timelines. Further details of the folder structure can be found in the [Folder structure](#folder-structure) section below.

### Adding audio files to the library

You can add audio files to the dScaper library using the `store_audio` method. This method takes a file path and metadata as parameters. The metadata should be an instance of `DscaperAudio`. It defines library, label, and filename for storing the audio file. As most methods in dScaper, it returns a `DscaperJsonResponse` object that contains the result of the operation. More details about the `DscaperJsonResponse` can be found in the [Dscaper class methods](#dscaper-class-methods) section below.

```python
from scaper.dscaper_datatypes import DscaperAudio

file_path = "/path/to/audio/file.wav"
metadata = DscaperAudio(library="my_library", label="my_label", filename="my_file.wav")
resp = dsc.store_audio(file_path, metadata)

if (resp.status == "success"):
    print("Audio file stored successfully.")
else:
    print(f"Error storing audio file: {resp.content}")
```

### Assemble timelines
To assemble a timeline, you first create an empty timeline using the `create_timeline` method. This method takes a `DscaperTimeline` instance as a parameter which allows you to specify the name, duration, and description of the timeline. The name of the timeline should be unique and will be used to reference the timeline later. dScaper will refuse to create a timeline with the same name as an existing one.

```python
from scaper.dscaper_datatypes import DscaperTimeline

timeline_metadata = DscaperTimeline(name="my_timeline", duration=10.0, description="Test timeline")
dsc.create_timeline(timeline_metadata)
```
#### Adding background sounds
Now you can add background sounds and events to the timeline. Background sounds are added using the `add_background` method that takes a `DscaperBackground` instance as a parameter. Paramters of type `list[str]` are used to represent distributions in the format described in the [Distribution lists](#distribution-lists) section below.

Attributes of `DscaperBackground`:
  - `library (str)`: The name of the audio library from which the background is sourced.
  - `label (list[str])`: The label(s) describing the background audio. Defaults to `['choose', '[]']` which will randomly choose one label in the library.
  - `source_file (list[str])`: The file(s) from which the background audio is taken. Defaults to `['choose', '[]']` which will randomly choose one file in the library.
  - `source_time (list[str])`: The time specification for the source audio. Defaults to `['const', '0']` which means the background starts at the beginning of the source file.


```python
from scaper.dscaper_datatypes import DscaperBackground

background_metadata = DscaperBackground(..)
dsc.add_background("my_timeline", background_metadata)
```
#### Adding events

Events are added using the `add_event` method that takes a `DscaperEvent` instance as a parameter. Again, paramters of type `list[str]` represent distributions (see [Distribution lists](#distribution-lists)). 

Attributes of `DscaperEvent`:
  - `library (str)`: The name of the audio library from which the event is sourced.
  - `label (list[str])`: The label from which the event is sourced. Defaults to `['choose', '[]']` which will randomly choose one label in the library.
  - `source_file (list[str])`: The source audio file for the event, typically in the form `['choose', '[]']` which will randomly choose one file in the library.
  - `source_time (list[str])`: The start time within the source file, typically in the form `['const', '0']` which means the event starts at the beginning of the source file.
  - `event_time (list[str])`: The time at which the event occurs in the timeline, typically in the form `['const', '0']` which means the event starts at the beginning of the timeline.
  - `event_duration (list[str]) | None`: The duration of the event. Can be set to `None` to use the duration of the source file, or specified as a distribution like `['const', '5']` which means the event lasts for 5 seconds. If not set and no source file is specified, it defaults to `['const', '5']`.
  , typically in the form `['const', '5']` which means the event lasts for 5 seconds.
  - `snr (list[str])`: The signal-to-noise ratio for the event, typically in the form `['const', '0']`.
  - `pitch_shift (list[str] | None)`: Optional pitch shift parameters for the event. Defaults to `None`.
  - `time_stretch (list[str] | None)`: Optional time stretch parameters for the event. Defaults to `None`.
  - `position (str | None)`: Optional position of the event (e.g., seat_1, seat_2, door, window). Defaults to `None`. This allows you to categorize events in the timeline and write them to separate audio files when generating the timeline. This is useful for applying different post-processings, e.g. applying different room acoustics to different speakers and sound sources.

```python
from scaper.dscaper_datatypes import DscaperEvent

event_metadata = DscaperEvent(..)
dsc.add_event("my_timeline", event_metadata)
```
### Generating timelines
Once you have added all the necessary background sounds and events to the timeline, you can generate the audio using the `generate_timeline` method. This method takes a `DscaperGenerate` instance as a parameter.
It represents the configuration and metadata for a soundscape generation process. The method returns a `DscaperJsonResponse` object containing the ID of the generated timeline. This ID is used to reference the generated audio later.

Attributes of `DscaperGenerate`:
  - `seed (int)`: Random seed used for reproducibility of the generation process. Default is 0.
  - `ref_db (int)`: Reference decibel level for the generated audio. Default is -20.
  - `reverb (float)`: Amount of reverb to apply to the generated audio. Default is 0.0.
  - `save_isolated_events (bool)`: Whether to save isolated audio files for each event. Default is False.
  - `save_isolated_positions (bool)`: Whether to save isolated audio files for each event position. Default is False.

```python
from scaper.dscaper_datatypes import DscaperGenerate

generate_metadata = DscaperGenerate(...)
resp = dsc.generate_timeline("my_timeline", generate_metadata)

content = DscaperGenerate(**resp.content)
print("ID:",content.id)  
```

### Reading generated timelines
You can retrieve the generated audio and metadata using the `get_generated_timeline_by_id` method. This method takes the timeline name and the generated ID as parameters. It returns a `DscaperJsonResponse` object containing the generated audio and metadata.

```python
resp = dsc.get_generated_timeline_by_id("my_timeline", content.id)
if resp.status == "success":
    content = DscaperGenerate(**resp.content)
    print(content.generated_files)  
```

You can also download all generated files as archive using `get_generated_files`. This method takes the timeline name and the generated ID as parameters. It returns a `DscaperJsonResponse` object containing the archive file.

```python
resp = dsc.get_generated_files("restaurant_timeline", id)
if resp.status == "success":
    filename = f"generated_files_{id}.zip"
    with open(filename, 'wb') as f:
        if resp.content is not None:
            if isinstance(resp.content, bytes):
                f.write(resp.content)
            else:
                raise TypeError("resp.content is not of type bytes")
        else:
            print("No content to write to file.")
```          

### dScaper class methods
Here is a complete list of the methods available in the `Dscaper` class. Most methods return a `DscaperJsonResponse` object, which contains the result of the operation and any relevant metadata. It has the following attributes:

- `status`: The status of the operation (e.g., "success", "error").
- `status_code`: The HTTP status code of the response (e.g., 200, 400).
- `content`: The main content of the response. This depends on the method. See below for details.
- `media_type`: The media type of the response content (e.g., "application/json", "text/plain").


| Method | Description |
|--------|-------------|
| `store_audio(file, metadata, update=False)` | Store an audio file and its metadata in the library. Supports file upload and update. Returns a `DscaperJsonResponse`. Content has type `DscaperAudio` and contains all data stored. |
| `read_audio(library, label, filename)` | Retrieve an audio file or its metadata from the library. Returns a `DscaperApiResponse` with content having the audio data. |
| `create_timeline(properties)` | Create a new timeline with specified properties. Returns a `DscaperJsonResponse`. Content is of type `DscaperTimeline`  and contains all data stored.|
| `add_background(timeline_name, properties)` | Add a background sound to a timeline. Returns a `DscaperJsonResponse`. Content is of type `DscaperBackground` and contains all data stored.|
| `add_event(timeline_name, properties)` | Add an event to a timeline. Returns a `DscaperJsonResponse`. Content is of type `DscaperEvent` and contains all data stored. |
| `generate_timeline(timeline_name, properties)` | Generate audio for a timeline using the provided generation parameters. Returns a `DscaperJsonResponse`. Content is of type `DscaperGenerate` and contains all data stored.|
| `get_dscaper_base_path()` | Returns the base path used for libraries and timelines as string. |
| `get_libraries()` | List all available audio libraries. Returns a `DscaperJsonResponse`. Content is a list of strings. |
| `get_filenames(library, label)` | List all filenames within a specific library and label. Returns a `DscaperJsonResponse`. Content is a list of strings.|
| `get_labels(library)` | List all labels within a specific library. Returns a `DscaperJsonResponse`. Content is a list of strings. |
| `list_timelines()` | List all timelines and their metadata. Returns a `DscaperJsonResponse`. Content is of type `DscaperTimelines`. |
| `list_backgrounds(timeline_name)` | List all backgrounds in a specified timeline. Returns a `DscaperJsonResponse`. Content is of type `DscaperBackgrounds`. |
| `list_events(timeline_name)` | List all events in a specified timeline. Returns a `DscaperJsonResponse`. Content is of type `DscaperEvents`. |
| `get_generated_timelines(timeline_name)` | List all generated outputs for a specified timeline. Returns a `DscaperJsonResponse`. Content is of type `DscaperGenerations`.|
| `get_generated_timeline_by_id(timeline_name, generate_id)` | Retrieve details of a specific generated output by its ID. Returns a `DscaperJsonResponse`. Content is of type `DscaperGenerate` and contains all data stored. |
| `get_generated_file(timeline_name, generate_id, file_name)` | Download a specific generated file (audio or metadata) by name. Returns a `DscaperJsonResponse`. Content is of type `DscaperGenerate` and contains all data stored. |
| `get_generated_files(timeline_name, generate_id)` | Download all generated files as an archive. Returns a `DscaperJsonResponse`. Content is of type `bytes` containing the archive data (zip). |


## Web API
The dScaper Web API provides a RESTful interface for interacting with dScaper functionality over HTTP. The API is implemented in the `web/api` directory and allows you to manage libraries, timelines, audio files, and trigger audio generation remotely. For development, you can run the API server using FastAPI dev server:

```bash
> fastapi dev main.py
```

There is a [postman](https://www.postman.com/) collection available in the `docs` directory that contains all endpoints and example requests. You can import this collection into Postman to test the API.

### Audio API

The Audio API provides endpoints for managing audio libraries, labels, and files. It allows you to upload, update, list, and retrieve audio files and their metadata.

#### Endpoints

- `POST /api/v1/audio/{library}/{label}/{filename}`  
    Upload a new audio file and its metadata to a specific library and label.  
    **Path parameters:**  
      - `library` (str): The library to store the audio in.  
      - `label` (str): The label for the audio file.  
      - `filename` (str): The name of the audio file.  
    **Request body (multipart/form-data):**  
      - `file` (bytes): The audio file to be uploaded.  
      - `sandbox` (str): JSON string containing sandbox data (metadata).  
    Returns the stored audio's metadata.  
    Errors: 400 if the file is empty/invalid or already exists.

- `PUT /api/v1/audio/{library}/{label}/{filename}`  
    Update an existing audio file and its metadata.  
    **Path parameters:**  
      - `library` (str): The library containing the audio.  
      - `label` (str): The label of the audio file.  
      - `filename` (str): The name of the audio file.  
    **Request body (multipart/form-data):**  
      - `file` (bytes): The new audio file to replace the existing one.  
      - `sandbox` (str): JSON string containing updated sandbox data (metadata).  
    Returns the updated audio's metadata.  
    Errors: 400 if the file is empty/invalid or does not exist.

- `GET /api/v1/audio/`  
    List all available audio libraries.  
    **Response:** List of library names.

- `GET /api/v1/audio/{library}`  
    List all labels within a specific library.  
    **Path parameters:**  
      - `library` (str): The library to get labels from.  
    **Response:** List of label names.  
    Errors: 404 if the library does not exist.

- `GET /api/v1/audio/{library}/{label}`  
    List all filenames within a specific label of a library.  
    **Path parameters:**  
      - `library` (str): The library to get filenames from.  
      - `label` (str): The label to get filenames from.  
    **Response:** List of filenames.  
    Errors: 404 if the library or label does not exist.

- `GET /api/v1/audio/{library}/{label}/{filename}`  
    Retrieve metadata or the audio file itself for a given library, label, and filename.  
    **Path parameters:**  
      - `library` (str): The library of the audio file.  
      - `label` (str): The label of the audio file.  
      - `filename` (str): The name of the audio file or its metadata.  
    **Response:** The audio file or its metadata.  
    Errors: 404 if the audio file does not exist.

All responses are wrapped in a standard response object. Errors such as missing files or libraries return appropriate HTTP status codes (e.g., 400, 404).

### Timeline API
The Timeline API provides endpoints for creating and managing timelines, adding backgrounds and events, and generating audio. Each timeline represents a sequence of audio events and backgrounds, which can be generated into audio files.

#### Endpoints

- `POST /api/v1/timeline/{timeline_name}`  
    Create a new timeline with the specified name and properties.  
    **Path parameters:**  
      - `timeline_name` (str): The name of the timeline to create.  
    **Request body (application/json):**  
      - `duration` (float): Duration of the timeline in seconds.  
      - `description` (str, optional): Description of the timeline.  
      - `sandbox` (dict, optional): Additional metadata or sandbox data.  
    **Response:** Confirmation and details of the created timeline.

- `POST /api/v1/timeline/{timeline_name}/background`  
    Add a background sound to the specified timeline.  
    **Path parameters:**  
      - `timeline_name` (str): The name of the timeline.  
    **Request body (application/json):**  
      - Background properties as defined by `DscaperBackground`.  
    **Response:** Confirmation and details of the added background.

- `POST /api/v1/timeline/{timeline_name}/event`  
    Add an event to the specified timeline.  
    **Path parameters:**  
      - `timeline_name` (str): The name of the timeline.  
    **Request body (application/json):**  
      - Event properties as defined by `DscaperEvent`.  
    **Response:** Confirmation and details of the added event.

- `POST /api/v1/timeline/{timeline_name}/generate`  
    Generate audio for the specified timeline using provided generation parameters.  
    **Path parameters:**  
      - `timeline_name` (str): The name of the timeline.  
    **Request body (application/json):**  
      - Generation parameters as defined by `DscaperGenerate`.  
    **Response:** Confirmation and details of the generation process.

- `GET /api/v1/timeline/`  
    List all available timelines.  
    **Response:** List of timeline names and metadata.

- `GET /api/v1/timeline/{timeline_name}/background`  
    List all backgrounds in the specified timeline.  
    **Path parameters:**  
      - `timeline_name` (str): The name of the timeline.  
    **Response:** List of backgrounds.

- `GET /api/v1/timeline/{timeline_name}/event`  
    List all events in the specified timeline.  
    **Path parameters:**  
      - `timeline_name` (str): The name of the timeline.  
    **Response:** List of events.

- `GET /api/v1/timeline/{timeline_name}/generate`  
    List all generated outputs for the specified timeline.  
    **Path parameters:**  
      - `timeline_name` (str): The name of the timeline.  
    **Response:** List of generated outputs.

- `GET /api/v1/timeline/{timeline_name}/generate/{generate_id}`  
    Retrieve all files generated for a specific timeline by its ID as an archive.
    **Path parameters:**  
      - `timeline_name` (str): The name of the timeline.  
      - `generate_id` (str): The ID of the generated output.  
    **Response:** Details of the generated output.

- `GET /api/v1/timeline/{timeline_name}/generate/{generate_id}/{file_name}`  
    Download a specific generated file (e.g., audio or metadata) by name.  
    **Path parameters:**  
      - `timeline_name` (str): The name of the timeline.  
      - `generate_id` (str): The ID of the generated output.  
      - `file_name` (str): The name of the file to download.  
    **Response:** The requested file or its metadata.

All endpoints return responses wrapped in a standard response object. Errors such as missing timelines or invalid parameters return appropriate HTTP status codes.
"""

## Distribution lists
dScaper supports the same distributions as the original Scaper library. Instead of tuples, it uses lists to represent distributions. All list elements must be of type string. The following distributions are supported:

- `['const', value]`: Constant value distribution.
- `['choose', list]`: Uniformly sample from a finite set of values given by `list`.
- `['choose_weighted', list, weights]`: Sample from a finite set of values given by `list` with specified `weights` for each value.
- `['uniform', min, max]`: Uniform distribution between `min` and `max`.
- `['normal', mean, std]`: Normal distribution with specified `mean` and `std` (standard deviation).
- `['truncnorm', mean, std, min, max]`: Truncated normal distribution with specified `mean`, `std`, and limits between `min` and `max`.

If you use an empty list `[]`, it is interpreted as a distribution that samples from all available values. For example, if you specify `['choose', '[]']` for the label, it will sample from all available values in the library.

## Folder structure
The dScaper library and timelines are stored in the `libraries` and `timelines` directories, respectively. The structure for `libraries` is as follows:

```/path/to/dscaper/data/
└── libraries
    ├── [library_1_name]
    │   ├── [label_1]
    │   │   ├── [audio_file_1.wav]
    │   │   ├── [audio_file_1.json]
    │   │   ├── [audio_file_2.wav]  
    │   │   └── [...]   
    │   ├── [label_2]
    │   │   ├── [audio_file_2.wav]
    │   │   └── [audio_file_2.json]
    │   └── [...]
    └── [library_2_name]
        └── [...]
```
Timelines define the structure of the generated audio. They are organized as follows:
```
└── timelines
    ├── [timeline_1_name]
    │   ├── timeline.json
    │   ├── background
    │   │   ├── [background_1_id].json
    │   │   ├── [background_2_id].json
    │   │   └── [...]
    │   ├── events
    │   │   ├── [event_1_id].json
    │   │   ├── [event_2_id].json
    │   │   └── [...]
    │   └── generate
    │       ├── [generation_1_id]
    │       │    ├── generate.json
    │       │    ├── soundscape.wav
    │       │    ├── soundscape.jams
    │       │    └── soundscape.text
    │       └── [...]
    └── [timeline_2_name]
        └── [...]
```
When generating with `save_isolated_positions` set to `True`, an additional subfolder `soundscape_positions` is created in the `[generation_id]` folder. The structure is as follows:


```
   └── generate
       ├── [generation_1_id]
       │    ├── generate.json 
       │    ├── soundscape.wav - complete soundscape with all events
       │    ├── ..
       │    └── soundscape_positions
       │         ├── [position_1].wav - soundscape with only events of position 1
       │         ├── [position_1].jams - JAMS file for event position 1
       │         ├── [position_2].wav - soundscape with only events of position 2
       │         ├── [position_2].jams - JAMS file for event position 2
       │         ├── [...]
       │         └── no_position.wav - soundscape with all events that do not have an event position assigned
       └── [...]
```
You can also generate with `save_isolated_events` set to `True`. In this case, a separate audio file is created for each event in the soundscape. The audio files are stored in a subfolder `soundscape_events` within the `[generation_id]` folder. 

## Misc

### Jams to RTTM
The file `misc/jams_to_rttm` contains a script that converts JAMS files to RTTM format. This is a format that can be used for evaluation or further processing. Example usage:

```python
import misc.jams_to_rttm as jams2rttm

jams_path = "/path/to/input.jams"
rttm_path = "/path/to/output.rttm"
jams2rttm.jams_to_rttm(jams_path, rttm_path)
```
