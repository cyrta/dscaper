# dScaper

![dScaper logo](/docs/dScaper-logo.png)

*A [Scaper](https://github.com/justinsalamon/scaper) fork optimized  audio generation pipelines.* 

dScaper was developped during [JSALT25](https://jsalt2025.fit.vut.cz/) Workshop by David Grünert. dScaper offers an 
alternative API for accessing Scaper that is optimized for the usage pipelines. Please refer to 
[Scaper documentation](http://scaper.readthedocs.io/) for details of the original Scaper API.

## Architecture and key features

dScaper can eighter be use as python module or as separate server. In both variants, dScaper not only handles timeline generation, but it also stores and manages audio files.

![architecture overview](docs/dscaper_architecture.drawio.svg)


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
You can generate timelines using the `create_timeline` method. This method takes a `DscaperTimeline` instance as a parameter. The `DscaperTimeline` class allows you to specify the name, duration, and description of the timeline.

```python
from scaper.dscaper_datatypes import DscaperTimeline

timeline_metadata = DscaperTimeline(name="my_timeline", duration=10.0, description="Test timeline")
dsc.create_timeline(timeline_metadata)
```
Now you can add background sounds and events to the timeline. Background sounds are added using the `add_background` method that takes a `DscaperBackground` instance as a parameter. 

```python
from scaper.dscaper_datatypes import DscaperBackground
background_metadata = DscaperBackground(..)
```

Events are added using the `add_event` method that takes a `DscaperEvent` instance as a parameter.
```python
from scaper.dscaper_datatypes import DscaperEvent
event_metadata = DscaperEvent(..)
```
### Generating timelines
Once you have added all the necessary background sounds and events to the timeline, you can generate the audio using the `generate_timeline` method. This method takes a `DscaperGenerate` instance as a parameter.

```python
from scaper.dscaper_datatypes import DscaperGenerate

generate_metadata = DscaperGenerate(...)
dsc.generate_timeline("my_timeline", generate_metadata)
```

## Web API
