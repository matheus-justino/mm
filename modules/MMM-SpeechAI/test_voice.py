import time, os, pyaudio, wave

from transformers import pipeline
from pyannote.audio import Pipeline
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import soundfile as sf

processor = WhisperProcessor.from_pretrained("openai/whisper-small")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")
forced_decoder_ids = processor.get_decoder_prompt_ids(language="portuguese", task="transcribe")
speech_detector = Pipeline.from_pretrained("pyannote/voice-activity-detection", use_auth_token="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")
classifier = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")

audio_path = os.getcwd()+"\\speechai\\speech-audio.wav"

def get_voice():
    while True:
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 48000
        CHUNK = 1024
        RECORD_SECONDS = 5
        WAVE_OUTPUT_FILENAME = os.getcwd()+"\\speechai\\speech-audio.wav"

        audio = pyaudio.PyAudio()

        # start Recording
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)


        # stop Recording
        stream.stop_stream()
        stream.close()
        audio.terminate()

        wave_file = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wave_file.setnchannels(CHANNELS)
        wave_file.setsampwidth(audio.get_sample_size(FORMAT))
        wave_file.setframerate(RATE)
        wave_file.writeframes(b''.join(frames))
        wave_file.close()

        array, sampling_rate = sf.read("./speechai/speech-audio.wav")
        input_features = processor(array, sampling_rate=16000, return_tensors="pt").input_features
        predicted_ids = model.generate(input_features, forced_decoder_ids=forced_decoder_ids)
        transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)

        if len(transcription) > 0:
            command_split = transcription[0].split('.')[0].split(" ")

            if "So" in command_split or "Sol" in command_split or "Só" in command_split or "Sól" in command_split:
                print({'action': 'turn-on-sol', 'audio-to-text': transcription[0]})
            else:
                print({'action': 'voice-activity-log', 'audio-to-text': transcription[0]})

get_voice()
