# dScaper

![dScaper logo](/docs/dScaper-logo.png)

*A [Scaper](https://github.com/justinsalamon/scaper) fork optimized for audio generation pipelines.* 

dScaper was developped during [JSALT25](https://jsalt2025.fit.vut.cz/) Workshop by David Grünert. dScaper offers an 
alternative API for accessing Scaper that is optimized for the usage pipelines. Please refer to 
[Scaper documentation](http://scaper.readthedocs.io/) for details of the original Scaper API.

## Table of Contents

- [Architecture and key features](#architecture-and-key-features)
- [Installation](#installation)
- [Python API](#python-api)
  - [Adding audio files to the library](#adding-audio-files-to-the-library)
  - [Assemble timelines](#assemble-timelines)
  - [Generating timelines](#generating-timelines)
  - [Dscaper class methods](#dscaper-class-methods)
- [Web API](#web-api)
  - [Audio API](#audio-api)
  - [Timeline API](#timeline-api)
- [Distribution lists](#distribution-lists)


## Architecture and key features

dScaper can eighter be use as python module or as separate server. In both variants, dScaper not only handles timeline generation, but it also stores and manages audio files.

![architecture overview](docs/dscaper_architecture.drawio.svg)

The main features of dScaper are:
- **Audio library management**: dScaper allows you to store and manage audio files in a structured way. Audio files are organized into libraries and labels, making it easy to retrieve and use them in timelines.
- **Timeline management**: dScaper allows you to create and manage timelines, which define the structure of the generated audio. Timelines can include background sounds and events, which are used to generate the final audio output.
- **Audio generation**: dScaper can generate audio based on the defined timelines. It stores the generated audio files along with their metadata for each run, making it easy to retrieve and use them later.
- **Web API and Python API**: dScaper provides a RESTful Web API for remote access and management of audio libraries and timelines. It also offers a Python API for programmatic access, making it easy to integrate dScaper into your applications or workflows.


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
git clone https://github.com/cyrta/drender.git
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

dScaper will create two subfolders in the specified path: `libraries` and `timelines` if they do not already exist. 

```/path/to/dscaper/data/
├── libraries
│   ├── [library_data...]
├── timelines
│   ├── [timeline_data...]
```
Librarys are used to store audio files and their metadata. They are organized as follows: 

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

### Adding audio files to the library

You can add audio files to the dScaper library using the `store_audio` method. This method takes a file path and metadata as parameters. The metadata should be an instance of `DscaperAudio`.

```python
from scaper.dscaper_datatypes import DscaperAudio

file_path = "/path/to/audio/file.wav"
metadata = DscaperAudio(library="my_library", label="my_label", filename="my_file.wav")
dsc.store_audio(file_path, metadata)
```
### Assemble timelines
To assemble a timeline, you first create an empty timeline using the `create_timeline` method. This method takes a `DscaperTimeline` instance as a parameter which allows you to specify the name, duration, and description of the timeline. The name of the timeline should be unique and will be used to reference the timeline later. dScaper will refuse to create a timeline with the same name as an existing one.

```python
from scaper.dscaper_datatypes import DscaperTimeline

timeline_metadata = DscaperTimeline(name="my_timeline", duration=10.0, description="Test timeline")
dsc.create_timeline(timeline_metadata)
```
Now you can add background sounds and events to the timeline. Background sounds are added using the `add_background` method that takes a `DscaperBackground` instance as a parameter. DscaperBackground represents a background audio element in the Dscaper system. Paramters of type `list[str]` are used to represent distributions in the format described in the [Distribution lists](#distribution-lists) section below.


Attributes of `DscaperBackground`:
  - `library (str)`: The name of the audio library from which the background is sourced.
  - `label (list[str])`: The label(s) describing the background audio. Defaults to `['choose', '[]']`.
  - `source_file (list[str])`: The file(s) from which the background audio is taken. Defaults to `['choose', '[]']`.
  - `source_time (list[str])`: The time specification for the source audio. Defaults to `['const', '0']`.


```python
from scaper.dscaper_datatypes import DscaperBackground
background_metadata = DscaperBackground(..)
```

Events are added using the `add_event` method that takes a `DscaperEvent` instance as a parameter. DscaperEvent represents a single event in a soundscape timeline. Paramters of type `list[str]` are used to represent distributions in the format described in the [Distribution lists](#distribution-lists) section below.

Attributes of `DscaperEvent`:
  - `library (str)`: The name of the audio library from which the event is sourced.
  - `label (list[str])`: The label or category for the event, typically in the form `['choose', '[]']`.
  - `source_file (list[str])`: The source audio file for the event, typically in the form `['choose', '[]']`.
  - `source_time (list[str])`: The start time within the source file, typically in the form `['const', '0']`.
  - `event_time (list[str])`: The time at which the event occurs in the timeline, typically in the form `['const', '0']`.
  - `event_duration (list[str])`: The duration of the event, typically in the form `['const', '5']`.
  - `snr (list[str])`: The signal-to-noise ratio for the event, typically in the form `['const', '0']`.
  - `pitch_shift (list[str] | None)`: Optional pitch shift parameters for the event. Defaults to `None`.
  - `time_stretch (list[str] | None)`: Optional time stretch parameters for the event. Defaults to `None`.
  - `event_type (str | None)`: Optional type of the event (e.g., speakerA, speakerB, soundSource1). Defaults to `None`.

```python
from scaper.dscaper_datatypes import DscaperEvent
event_metadata = DscaperEvent(..)
```
### Generating timelines
Once you have added all the necessary background sounds and events to the timeline, you can generate the audio using the `generate_timeline` method. This method takes a `DscaperGenerate` instance as a parameter.
it Represents the configuration and metadata for a soundscape generation process.

Attributes of `DscaperGenerate`:
  - `seed (int)`: Random seed used for reproducibility of the generation process. Default is 0.
  - `ref_db (int)`: Reference decibel level for the generated audio. Default is -20.
  - `reverb (float)`: Amount of reverb to apply to the generated audio. Default is 0.0.
  - `save_isolated_events (bool)`: Whether to save isolated audio files for each event. Default is False.
  - `save_isolated_eventtypes (bool)`: Whether to save isolated audio files for each event type. Default is False.

```python
from scaper.dscaper_datatypes import DscaperGenerate

generate_metadata = DscaperGenerate(...)
dsc.generate_timeline("my_timeline", generate_metadata)
```

### Dscaper class methods
Here is a complete list of methods available in the `Dscaper` class:

| Method | Description |
|--------|-------------|
| `get_dscaper_base_path()` | Returns the base path used for libraries and timelines. |
| `store_audio(file, metadata, update=False)` | Store an audio file and its metadata in the library. Supports file upload and update. |
| `read_audio(library, label, filename)` | Retrieve an audio file or its metadata from the library. |
| `get_libraries()` | List all available audio libraries. |
| `get_filenames(library, label)` | List all filenames within a specific library and label. |
| `get_labels(library)` | List all labels within a specific library. |
| `create_timeline(properties)` | Create a new timeline with specified properties. |
| `add_background(name, properties)` | Add a background sound to a timeline. |
| `add_event(name, properties)` | Add an event to a timeline. |
| `generate_timeline(name, properties)` | Generate audio for a timeline using the provided generation parameters. |
| `list_timelines()` | List all timelines and their metadata. |
| `list_backgrounds(name)` | List all backgrounds in a specified timeline. |
| `list_events(name)` | List all events in a specified timeline. |
| `get_generated_timelines(name)` | List all generated outputs for a specified timeline. |
| `get_generated_timeline_by_id(name, generate_id)` | Retrieve details of a specific generated output by its ID. |
| `get_generated_file(name, generate_id, file_name)` | Download a specific generated file (audio or metadata) by name. |
| `_get_distribution_tuple(distribution)` | Helper: Convert a distribution list to a tuple for Scaper compatibility. |
| `_string_to_list(string)` | Helper: Convert a string representation of a list to a Python list. |




## Web API
The dScaper Web API provides a RESTful interface for interacting with dScaper functionality over HTTP. The API is implemented in the `web/api` directory and allows you to manage libraries, timelines, audio files, and trigger audio generation remotely.

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
    Retrieve details of a specific generated output by its ID.  
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
