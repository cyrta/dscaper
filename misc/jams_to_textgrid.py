import mytextgrid
import json

def jams_to_textgrid(jams_path, textgrid_path):
    """
    Convert a JAMS file to a TextGrid file.

    Args:
        jams_path (str): Path to the input JAMS file.
        textgrid_path (str): Path to the output TextGrid file.
    """
    with open(jams_path, 'r') as jams_file:
        jams_data = json.load(jams_file)

    tg = mytextgrid.TextGrid(0, 100)

    scaper_data = None
    for annotation in jams_data['annotations']:
        audio_path = annotation['sandbox']['scaper']['audio_path']
        if annotation['namespace'] == 'scaper':
            scaper_data = annotation['data']
            break
    if scaper_data is None:
        raise ValueError("No 'scaper' namespace found in JAMS file.")
    
    speakers = set()
    for event in scaper_data:
        if 'speaker' in event['value'] and event['value']['speaker'] is not None:
            speakers.add(event['value']['speaker'])

    # print(f"Found speakers: {speakers}")
    tiers = {}
    for speaker in speakers:
        tiers[speaker] = tg.insert_tier(speaker)
    if 'no_speaker' not in tiers:
        tiers['no_speaker'] = tg.insert_tier('no_speaker')

    
    current_time = {}
    boundary_count = {}
    for speaker in speakers:
        current_time[speaker] = 0.0
        boundary_count[speaker] = 0

    for event in scaper_data:
        start_time = round(float(event['time']),3)
        duration = event['duration']
        value = event['value']
        if 'speaker' in value and value['speaker'] is not None:
            # print(f"Processing event: {value['speaker']} at {start_time} with duration {duration}")
            speaker = value['speaker']
            end_time = round(float(start_time + duration), 3)
            text = value['text']
            if start_time > current_time[speaker]:
                # print(f"Inserting boundary for {speaker} at {start_time} for no text")
                tiers[speaker].insert_boundary(start_time)
                current_time[speaker] = start_time
                start_time = current_time[speaker]
                boundary_count[speaker] += 1
            # print(f"Inserting boundary for {speaker} at {end_time} with text '{text}'")
            tiers[speaker].insert_boundary(end_time)
            current_time[speaker] = end_time
            tiers[speaker].set_text_at_index(boundary_count[speaker], text)
            boundary_count[speaker] += 1
            
    tg.describe()
    tg.write(textgrid_path)
    print(f"TextGrid file written to {textgrid_path}")
    