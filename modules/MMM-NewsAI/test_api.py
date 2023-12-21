import os
from pydub import AudioSegment
from pydub.playback import play

audio = AudioSegment.from_mp3("speechai/test.mp3")

play(audio)