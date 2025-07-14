import scaper
import os

path_to_audio = os.path.join('tests','data','audio')

soundscape_duration = 10.0
seed = 123
foreground_folder = os.path.join(path_to_audio, 'foreground')
background_folder = os.path.join(path_to_audio, 'background')
sc = scaper.Scaper(soundscape_duration, foreground_folder, background_folder)
sc.ref_db = -20

sc.add_background(label=('const', 'park'),
                  source_file=('choose', []),
                  source_time=('const', 0))
sc.add_event(label=('const', 'siren'),
             source_file=('choose', []),
             source_time=('const', 0),
             event_time=('uniform', 0, 9),
             event_duration=('truncnorm', 3, 1, 0.5, 5),
             snr=('normal', 10, 3),
             pitch_shift=('uniform', -2, 2),
             time_stretch=('uniform', 0.8, 1.2))
for _ in range(2):
    sc.add_event(label=('choose', ['car_horn', 'siren']),
                 source_file=('choose', []),
                 source_time=('const', 0),
                 event_time=('uniform', 0, 9),
                 event_duration=('truncnorm', 3, 1, 0.5, 5),
                 snr=('normal', 10, 3),
                 pitch_shift=None,
                 time_stretch=None)
for _ in range(2):
    sc.add_event(label=('const', 'human_voice'),
                 source_file=('choose', []),
                 source_time=('const', 0),
                 event_time=('uniform', 0, 9),
                 event_duration=('truncnorm', 3, 1, 0.5, 5),
                 snr=('normal', 10, 3),
                 pitch_shift=None,
                 time_stretch=None,
                 event_type='human')
audiofile = 'soundscape.wav'
jamsfile = 'soundscape.jams'
txtfile = 'soundscape.txt'
sc.generate(audiofile, jamsfile,
            allow_repeated_label=True,
            allow_repeated_source=True,
            reverb=0.1,
            disable_sox_warnings=True,
            no_audio=False,
            txt_path=txtfile)
