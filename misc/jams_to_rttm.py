import json
import os

def jams_to_rttm(jams_path: str, rttm_path: str):
    """
    Convert a JAMS file to an RTTM file.

    Args:
        jams_path (str): Path to the input JAMS file.
        rttm_path (str): Path to the output RTTM file.
    """
    with open(jams_path, 'r') as jams_file:
        jams_data = json.load(jams_file)

    with open(rttm_path, 'w') as rttm_file:
        for annotation in jams_data['annotations']:
            audio_path = annotation['sandbox']['scaper']['audio_path']
            if annotation['namespace'] == 'scaper':
                for event in annotation['data']:
                    start = event['time']
                    duration = event['duration']
                    value = event['value']
                    if value['speaker'] is not None:                            
                        print(f"SPEAKER {audio_path} 1 {start:.3f} {duration:.3f} <NA> <NA> {value['speaker']} <NA> <NA>")
                        rttm_file.write(f"SPEAKER {audio_path} 1 {start:.3f} {duration:.3f} <NA> <NA> {value['speaker']} <NA> <NA>\n")
