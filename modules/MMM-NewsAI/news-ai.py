import time, os
print({'action': 'initializing-model'})
from huggingsound import SpeechRecognitionModel
from transformers import pipeline

model = SpeechRecognitionModel("jonatasgrosman/wav2vec2-xls-r-1b-portuguese")
audio_paths = [os.getcwd()+'\\speechai\\call-estela-male.mp3']
# audio_paths = [gravação do microfone]
classifier = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
print({'action': 'initialized-model'})

estela_thresh_hold = ['estela', 'stela', 'stella', 'estel', 'tela', 'extela', 'istela', 'iztela']

class EstelaAI:
    def __init__(self):
        self.estela_on = False
        self.command = ""
        self.score = 0

    def get_command(self):
        def get_command_loop():
            command_audio = [os.getcwd()+'\\speechai\\cloth-male.mp3']
            transcriptions = model.transcribe(command_audio)
            
            sequence_to_classify = transcriptions[0]['transcription']
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
            transcriptions = model.transcribe(audio_paths)

            if len(transcriptions) > 0:
                if transcriptions[0]['transcription'] in estela_thresh_hold:
                    print({'action': 'turn-on-estela'})
                    # Gravar audio do usuário
                    time.sleep(3)
                    self.get_command()
        except Exception as e:
            print({'action': 'speechai-error'})

estela_ai = EstelaAI()
estela_ai.check_turn_on()
# got_it()