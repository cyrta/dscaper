import pytest

from scaper import dscaper
from scaper.dscaper import Dscaper
from scaper.dscaper_datatypes import *
import os
import tempfile
import shutil
import uuid
import json
import soundfile as sf
from scaper.dscaper_datatypes import (
    DscaperApiResponse,
    DscaperAudio,
    DscaperTimeline,
    DscaperBackground,
    DscaperEvent,
    DscaperGenerate,
)

@pytest.fixture
def temp_lib_base():
    temp_dir = tempfile.mkdtemp()
    print(f"*** Created temporary library base path: {temp_dir}")
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_init_creates_dirs(temp_lib_base):
    d = Dscaper(dscaper_base_path=temp_lib_base)
    assert os.path.exists(os.path.join(temp_lib_base, "timelines"))
    assert os.path.exists(os.path.join(temp_lib_base, "libraries"))

def test_init_raises_if_path_missing():
    with pytest.raises(FileNotFoundError):
        Dscaper(dscaper_base_path="/nonexistent/path/for/test")

def test_get_dscaper_base_path(temp_lib_base):
    d = Dscaper(dscaper_base_path=temp_lib_base)
    assert d.get_dscaper_base_path() == temp_lib_base

def test_store_audio_and_read_audio(temp_lib_base):
    d = Dscaper(dscaper_base_path=temp_lib_base)
    # Prepare dummy audio file (WAV header, not valid audio)
    # audio_bytes = b'RIFF$\x00\x00\x00WAVEfmt ' + b'\x10\x00\x00\x00\x01\x00\x01\x00' + b'\x40\x1f\x00\x00\x80>\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    metadata = DscaperAudio(
        library="lib1",
        label="label1",
        filename="test.wav"
    )
    # Should fail on invalid audio file (non-existing file)
    resp = d.store_audio("non-existing-file.wav", metadata)
    assert resp.status == "error"
    # Should fail on invalid audio file (length)
    invalid_file = os.path.join(os.getcwd(), "tests", "data", "library_inputs", "empty_audio.wav")
    resp = d.store_audio(invalid_file, metadata)
    assert resp.status == "error"
    # Should fail on invalid audio file (type)
    invalid_file2 = os.path.join(os.getcwd(), "tests", "data", "library_inputs", "invalid_audio.wav")
    resp = d.store_audio(invalid_file2, metadata)
    assert resp.status == "error"
    # test storing a valid audio file
    valid_file = os.path.join(os.getcwd(), "tests", "data", "library_inputs", "valid_audio.wav")
    # valid_bytes, _ = sf.read(file_path, dtype='int16')
    # valid_bytes = valid_bytes.tobytes()  # Convert to bytes
    metadata.filename = "valid.wav"
    resp = d.store_audio(valid_file, metadata)
    # print(f"*** Response: {resp}")
    assert resp.status == "success"
    # test storing valid audio bytes
    # valid_bytes, _ = sf.read(valid_file, dtype='int16')
    # valid_bytes = valid_bytes.tobytes()  # Convert to bytes
    # metadata.filename = "valid2.wav"
    # resp = d.store_audio(valid_bytes, metadata)
    # print(f"*** Response: {resp}")
    # assert resp.status == "success"
    # add already existing audio file
    resp = d.store_audio(valid_file, metadata)
    assert resp.status == "error"
    assert resp.status_code == 400
    # update existing audio file
    resp = d.store_audio(valid_file, metadata, update=True)
    assert resp.status == "success"
    # update non-existing audio file
    metadata.filename = "non-existing.wav"
    resp = d.store_audio(valid_file, metadata, update=True)
    assert resp.status == "error"
    assert resp.status_code == 404
    # Now test reading metadata
    resp2 = d.read_audio("lib1", "label1", "valid.json")
    assert resp2.status == "success"
    # Now test reading audio
    resp3 = d.read_audio("lib1", "label1", "valid.wav")
    assert resp3.status == "success"
    assert isinstance(resp3.content, bytes)
    # test reading non-existing audio
    resp4 = d.read_audio("lib1", "label1", "non-existing.wav")
    assert resp4.status == "error"
    assert resp4.status_code == 404
    # test reading non-existing metadata
    resp5 = d.read_audio("lib1", "label1", "non-existing.json")
    assert resp5.status == "error"
    assert resp5.status_code == 404

def test_get_libraries(temp_lib_base):
    test_lib_path = os.path.join(os.getcwd(), "tests", "data")
    d = Dscaper(dscaper_base_path=test_lib_path)
    # Test getting libraries
    resp = d.get_libraries()
    print(resp)
    assert resp.status == "success"
    libraries = resp.content
    assert isinstance(libraries, list)
    assert len(libraries) > 0
    assert "testlib" in libraries

def test_get_labels(temp_lib_base):
    test_lib_path = os.path.join(os.getcwd(), "tests", "data")
    d = Dscaper(dscaper_base_path=test_lib_path)
    # Test getting labels of non-existing library
    resp = d.get_labels("non-existing-lib")
    assert resp.status == "error"
    assert resp.status_code == 404
    # Test getting labels
    resp = d.get_labels("testlib")
    assert resp.status == "success"
    labels = resp.content
    assert isinstance(labels, list)
    assert len(labels) > 0
    assert "horn" in labels
    assert "horn2" in labels

def test_get_filenames(temp_lib_base):
    test_lib_path = os.path.join(os.getcwd(), "tests", "data")
    d = Dscaper(dscaper_base_path=test_lib_path)
    # Test getting filenames of non-existing library/label
    resp = d.get_filenames("non-existing-lib", "non-existing-label")
    assert resp.status == "error"
    assert resp.status_code == 404
    # Test getting filenames of non-existing label
    resp = d.get_filenames("testlib", "non-existing-label")
    assert resp.status == "error"
    assert resp.status_code == 404
    # Test getting filenames of existing library/label
    resp = d.get_filenames("testlib", "horn")
    assert resp.status == "success"
    filenames = resp.content
    print(filenames)
    print(resp)
    assert isinstance(filenames, list)
    assert len(filenames) > 0
    assert "17-CAR-Rolls-Royce-Horn.wav" in filenames
    assert "17-CAR-Rolls-Royce-Horn.json" in filenames

def test_create_timeline_and_list_timelines(temp_lib_base):
    d = Dscaper(dscaper_base_path=temp_lib_base)
    props = DscaperTimeline(duration=10.0, description="desc", name="timeline1")
    resp = d.create_timeline(props)
    assert resp.status == "success" 
    # Check if the timeline was created
    list_resp = d.list_timelines()
    assert list_resp.status == "success"
    timelines = DscaperTimelines.model_validate_json(json.dumps(list_resp.content))  
    assert isinstance(timelines, DscaperTimelines)
    assert len(timelines.timelines) > 0
    # get first timeline
    timeline = timelines.timelines[0]
    assert isinstance(timeline, DscaperTimeline)
    assert timeline.name == "timeline1"
    assert timeline.duration == 10.0
    assert timeline.description == "desc"
    assert "id" in timeline.model_dump()  # Check if ID is present
    assert "timestamp" in timeline.model_dump()  # Check if timestamp is present
    # check adding timeline with same name fails
    resp2 = d.create_timeline(props)
    assert resp2.status == "error"
    assert resp2.status_code == 400

def test_add_background_and_list_backgrounds(temp_lib_base):
    d = Dscaper(dscaper_base_path=temp_lib_base)
    # Create a timeline first
    props = DscaperTimeline(duration=10.0, description="desc", name="timeline1")
    resp = d.create_timeline(props)
    assert resp.status == "success"
    # Add audio
    audio_file = os.path.join(os.getcwd(), "tests", "data", "library_inputs", "valid_audio.wav")
    metadata = DscaperAudio(
        library="my_lib",
        label="my_label",
        filename="audio.wav",
    )
    resp = d.store_audio(audio_file, metadata)
    assert resp.status == "success"
    # add background
    bg = DscaperBackground(library="my_lib")
    resp = d.add_background("timeline1", bg)
    assert resp.status == "success"
    assert resp.content is not None
    bg_data = resp.content
    assert "id" in bg_data
    assert "library" in bg_data
    assert bg_data["library"] == "my_lib"
    # list backgrounds
    list_resp = d.list_backgrounds("timeline1")
    assert list_resp.status == "success"
    backgrounds = DscaperBackgrounds.model_validate_json(json.dumps(list_resp.content))
    assert isinstance(backgrounds, DscaperBackgrounds)
    assert len(backgrounds.backgrounds) > 0
    # Check if the first background has the expected properties
    background = backgrounds.backgrounds[0]
    assert isinstance(background, DscaperBackground)
    assert background.library == "my_lib"
    # add background to a non-existing timeline
    resp2 = d.add_background("non-existing-timeline", bg)
    assert resp2.status == "error"
    assert resp2.status_code == 404
    # list backgrounds of a non-existing timeline
    list_resp2 = d.list_backgrounds("non-existing-timeline")
    assert list_resp2.status == "error"
    assert list_resp2.status_code == 404

def test_add_event_and_list_events(temp_lib_base):
    d = Dscaper(dscaper_base_path=temp_lib_base)
    # Create a timeline first
    props = DscaperTimeline(duration=10.0, description="desc", name="timeline2")
    resp = d.create_timeline(props)
    assert resp.status == "success"
    # Add audio
    audio_file = os.path.join(os.getcwd(), "tests", "data", "library_inputs", "valid_audio.wav")
    metadata = DscaperAudio(
        library="my_lib",
        label="my_label",
        filename="audio.wav",
    )
    resp = d.store_audio(audio_file, metadata)
    assert resp.status == "success"
    # add event
    ev = DscaperEvent(library="my_lib")
    resp = d.add_event("timeline2", ev)
    assert resp.status == "success"
    assert resp.content is not None
    ev_data = resp.content
    assert "id" in ev_data
    assert "library" in ev_data
    assert ev_data["library"] == "my_lib"
    # list events
    list_resp = d.list_events("timeline2")
    assert list_resp.status == "success"
    events = DscaperEvents.model_validate_json(json.dumps(list_resp.content))
    assert isinstance(events, DscaperEvents)
    assert len(events.events) > 0
    # Check if the first event has the expected properties
    event = events.events[0]
    assert isinstance(event, DscaperEvent)
    assert event.library == "my_lib"
    assert "id" in event.model_dump()  # Check if ID is present
    assert "event_type" in event.model_dump()  # Check if event_type is present
    # add event to a non-existing timeline
    resp2 = d.add_event("non-existing-timeline", ev)
    assert resp2.status == "error"
    assert resp2.status_code == 404
    # list events of a non-existing timeline
    list_resp2 = d.list_events("non-existing-timeline")
    assert list_resp2.status == "error"
    assert list_resp2.status_code == 404

def test_generate_timeline(temp_lib_base):
    d = Dscaper(dscaper_base_path=temp_lib_base)
    # Create a timeline first
    props = DscaperTimeline(duration=10.0, description="desc", name="timeline3")
    resp = d.create_timeline(props)
    assert resp.status == "success"
    # Add audio
    audio_file = os.path.join(os.getcwd(), "tests", "data", "library_inputs", "valid_audio.wav")
    metadata = DscaperAudio(
        library="my_lib",
        label="my_label",
        filename="audio.wav",
    )
    resp = d.store_audio(audio_file, metadata)
    assert resp.status == "success"
    # add background
    bg = DscaperBackground(library="my_lib")
    resp = d.add_background("timeline3", bg)
    assert resp.status == "success"
    # add events
    ev = DscaperEvent(library="my_lib",event_type="speakerA")
    resp = d.add_event("timeline3", ev)
    assert resp.status == "success"
    ev = DscaperEvent(library="my_lib",event_type="speakerB")
    resp = d.add_event("timeline3", ev)
    assert resp.status == "success"
    # generate timeline
    gen_props = DscaperGenerate(seed=42, ref_db=-20, reverb=0.5)
    gen_resp = d.generate_timeline("timeline3", gen_props)
    assert gen_resp.status == "success"
    assert gen_resp.content is not None
    generated_data = DscaperGenerate.model_validate(gen_resp.content)
    assert generated_data.id is not None
    assert generated_data.timestamp > 0
    assert isinstance(generated_data.generated_files, list)
    assert len(generated_data.generated_files) > 0
    # ['soundscape.wav', 'soundscape.txt', 'soundscape.jams']
    assert "soundscape.wav" in generated_data.generated_files
    assert "soundscape.txt" in generated_data.generated_files
    assert "soundscape.jams" in generated_data.generated_files
    # generate timeline with other settings
    gen_props2 = DscaperGenerate(seed=123, ref_db=-30, reverb=0.2, save_isolated_eventtypes=True)
    gen_resp2 = d.generate_timeline("timeline3", gen_props2)
    assert gen_resp2.status == "success"
    assert gen_resp2.content is not None
    generated_data2 = DscaperGenerate.model_validate(gen_resp2.content)
    assert generated_data2.id is not None
    assert generated_data2.timestamp > 0
    assert isinstance(generated_data2.generated_files, list)
    assert len(generated_data2.generated_files) > 0
    assert "soundscape.wav" in generated_data2.generated_files
    # TODO: fix
    print("++++", generated_data2.generated_files)
    # generate none-existing timeline
    gen_resp3 = d.generate_timeline("non-existing-timeline", gen_props)
    assert gen_resp3.status == "error"
    assert gen_resp3.status_code == 404
    # get generated timelines
    gen_list_resp = d.get_generated_timelines("timeline3")
    assert gen_list_resp.status == "success"
    generated_timelines = DscaperGenerations.model_validate_json(json.dumps(gen_list_resp.content))
    assert isinstance(generated_timelines, DscaperGenerations)
    assert len(generated_timelines.generations) == 2
    # get non-existing timeline
    gen_list_resp2 = d.get_generated_timelines("non-existing-timeline")
    assert gen_list_resp2.status == "error"
    assert gen_list_resp2.status_code == 404
    # get generated timeline by ID
    gen_timeline_resp = d.get_generated_timeline_by_id("timeline3", generated_data.id)
    assert gen_timeline_resp.status == "success"
    assert gen_timeline_resp.content is not None
    # get generated timeline by non-existing ID
    gen_timeline_resp2 = d.get_generated_timeline_by_id("timeline3", "non-existing-id")
    assert gen_timeline_resp2.status == "error"
    assert gen_timeline_resp2.status_code == 404
    # get generated wav file
    gen_file_resp = d.get_generated_file("timeline3", generated_data.id, "soundscape.wav")
    assert gen_file_resp.status == "success"
    assert isinstance(gen_file_resp.content, bytes)
    # get non-existing generated wav file
    gen_file_resp2 = d.get_generated_file("timeline3", generated_data.id, "non-existing-file.wav")
    assert gen_file_resp2.status == "error"
    assert gen_file_resp2.status_code == 404
    # get generated wav file from non-existing timeline
    gen_file_resp3 = d.get_generated_file("non-existing-timeline", generated_data.id, "soundscape.wav")
    assert gen_file_resp3.status == "error"
    assert gen_file_resp3.status_code == 404
    # get generated jams file
    gen_jams_resp = d.get_generated_file("timeline3", generated_data.id, "soundscape.jams")
    assert gen_jams_resp.status == "success"
    # get generated txt file
    gen_txt_resp = d.get_generated_file("timeline3", generated_data.id, "soundscape.txt")
    assert gen_txt_resp.status == "success"

def test__get_distribution_tuple(temp_lib_base):
    # const
    d = Dscaper(dscaper_base_path=temp_lib_base)
    assert d._get_distribution_tuple(['const', '7']) == ('const', 7)
    assert d._get_distribution_tuple(['const', 'text']) == ('const', 'text')
    with pytest.raises(ValueError):
        d._get_distribution_tuple(['const', '1', '2'])
    with pytest.raises(ValueError):
        d._get_distribution_tuple(['const',{ 'invalid': 'format'}])
    # choose
    assert d._get_distribution_tuple(['choose', '[1,2,3]']) == ('choose', ['1', '2', '3'])
    with pytest.raises(ValueError):
        d._get_distribution_tuple(['choose', '[1,2,3]', 'extra'])
    # choose_weighted
    # TODO: check if this is correct
    assert d._get_distribution_tuple(['choose_weighted', '[1,2,3]', '[0.1,0.2,0.7]']) == ('choose_weighted', ['1', '2', '3'], ['0.1', '0.2', '0.7'])
    with pytest.raises(ValueError):
        # TODO: fix this
        # d._get_distribution_tuple(['choose_weighted', '[1,2,3]', '[0.1,0.2]'])
        d._get_distribution_tuple(['choose_weighted', '[1,2,3]'])
    # uniform
    assert d._get_distribution_tuple(['uniform', '1', '10']) == ('uniform', 1, 10)
    with pytest.raises(ValueError):
        d._get_distribution_tuple(['uniform', '1', '10', 'extra'])
    # normal
    assert d._get_distribution_tuple(['normal', '5', '2']) == ('normal', 5, 2)
    with pytest.raises(ValueError):
        d._get_distribution_tuple(['normal', '5', '2', 'extra'])
    # truncnorm
    assert d._get_distribution_tuple(['truncnorm', '5', '2', '1', '10']) == ('truncnorm', 5, 2, 1, 10)
    with pytest.raises(ValueError):
        d._get_distribution_tuple(['truncnorm', '5', '2', '1', '10', 'extra'])
    # invalidnormal
    with pytest.raises(ValueError):
        d._get_distribution_tuple(['invalidnormal', '5', '2'])
    # invalid format
    with pytest.raises(ValueError):
        d._get_distribution_tuple({'invalid_format'})


def test__string_to_list(temp_lib_base):
    d = Dscaper(dscaper_base_path=temp_lib_base)
    assert d._string_to_list("[a, b, c]") == ["a", "b", "c"]
    assert d._string_to_list("[]") == []
    assert d._string_to_list("a, b") == ["a", "b"]
    assert d._string_to_list("a") == ["a"]
    assert d._string_to_list("") == []
    with pytest.raises(ValueError):
        d._string_to_list(['a', 'b', 'c'])  
    # Test with quotes
    # assert d._string_to_list('["a", "b", "c"]') == ["a", "b", "c"]
    # assert d._string_to_list('"a"') == ["a"]



