"""
Script responsável pela detecção de comandos por voz da Sol.
"""

import time, os, pyaudio, wave

print({'action': 'initializing-model'})

# Opt 1
from transformers import pipeline
from pyannote.audio import Pipeline
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import soundfile as sf

# Opt 2
import speech_recognition as sr


processor = WhisperProcessor.from_pretrained("openai/whisper-small")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")
forced_decoder_ids = processor.get_decoder_prompt_ids(language="portuguese", task="transcribe")
speech_detector = Pipeline.from_pretrained("pyannote/voice-activity-detection", use_auth_token="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")
classifier = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")

audio_path = os.getcwd()+"\\speechai\\speech-audio.wav"

print({'action': 'initialized-model'})

class SolAI:
    def __init__(self):
        self.sol_on = False
        self.command = ""
        self.score = 0
        self.wav = None
        self.array = []
        self.sampling_rate = 16000
        self.input_features = {}
        self.predicted_ids = []
        self.transcription = ""
        self.voice_recording = False

    def get_command(self):
        def get_command_loop():           
            sequence_to_classify = self.transcription
            self.command = sequence_to_classify
            candidate_labels = ["cloth", "weather_and_climate", "news"]
            output = classifier(sequence_to_classify, candidate_labels, multi_label=True)

            if output['scores'][0] > 0.9:
                category = output['labels'][0]
                return category
            else:
                return 'unknown'

        try:
            running = True

            while running:
                category = get_command_loop()

                if category == 'cloth':
                    print({'action': 'cloth-module', 'audio_to_text': self.command})
                    running = False
                elif category == 'weather_and_climate':
                    print({'action': 'weather-module', 'audio_to_text': self.command})
                    running = False
                elif category == 'news':
                    print({'action': 'news-module', 'audio_to_text': self.command})
                    running = False
                else:
                    print({'action': 'command-not-recognized', 'audio_to_text': self.command})
                    running = False
        except Exception as e:
            print({'action': 'speechai-error', 'e': str(e)})

    def check_turn_on(self):
        try:
            array, sampling_rate = sf.read("./speechai/speech-audio.wav")
            input_features = processor(array, sampling_rate=16000, return_tensors="pt").input_features
            predicted_ids = model.generate(input_features, forced_decoder_ids=forced_decoder_ids)
            transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)

            self.array = array
            self.sampling_rate = sampling_rate
            self.input_features = input_features
            self.predicted_ids = predicted_ids
            self.transcription = transcription

            if len(transcription) > 0:
                command_split = transcription[0].split('.')[0].split(" ")

                if "So" in command_split or "Sol" in command_split or "Só" in command_split or "Sól" in command_split:
                    print({'action': 'turn-on-sol', 'audio-to-text': transcription[0]})
                    self.get_command()
                else:
                    print({'action': 'voice-activity-log', 'audio-to-text': transcription[0]})
                    
        except Exception as e:
            print({'action': 'speechai-error', 'e': e})

    def check_voice_activity(self):
        try:
            while True:
                FORMAT = pyaudio.paInt16
                CHANNELS = 1
                RATE = 16000
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
                self.wav = wave_file
                wave_file.close()

                output = speech_detector(os.getcwd()+'\\speechai\\speech-audio.wav')

                speech_regions = []

                for speech in output.get_timeline().support():
                    speech_regions.append(speech)

                if len(speech_regions) > 0:
                    self.check_turn_on()
                    print({'action': 'voice-activity'})
                    self.voice_recording = True
                else:
                    if self.voice_recording:
                        print({'action': 'voice-activity-off'})
                        self.voice_recording = False
        except Exception as e:
            print(e)

class SpeechAI:
    """
    Módulo responsável pela detecção de comandos por voz da Sol.

    `m_id` - ID/port do microfone usado para reconhecimento.

    """

    def init(self, m_id=0):
        self.r = sr.Recognizer()
        if m_id != 0:
            self.m = sr.Microphone(m_id)
        else:
            self.m = sr.Microphone()
        self.transcription = ""

    def voice_activity(self):
        """
        Função que ativa a detecção de comandos por voz da Sol.
        """

        def callback(recognizer, audio):
            try:
                self.transcription = recognizer.recognize_whisper(audio, model='small', language='portuguese')
            except sr.UnknownValueError:
                print({'action': 'voice-activity-off', 'code': 'could-not-understand'})
            except sr.RequestError as e:
                print({'action': 'voice-activity-off', 'code': 'request-error'})
            
        with self.m as source:
            self.r.adjust_for_ambient_noise(source)
            
        stop_listening = self.r.listen_in_background(self.m, callback)

        while True:
            time.sleep(10000)
        
        stop_listening(wait_for_stop=False)
        
# speech_ai = SpeechAI()
# speech_ai.voice_activity()