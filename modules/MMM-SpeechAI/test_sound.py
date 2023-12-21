import speech_recognition as sr
import time

def callback(recognizer, audio):
    try:
        print(recognizer.recognize_whisper(audio, model='small', language='portuguese'))
    except sr.UnknownValueError:
        print("couldn't understand.")
    except sr.RequestError as e:
        print("couldn't request.")

r = sr.Recognizer()
m = sr.Microphone()

with m as source:
    r.adjust_for_ambient_noise(source)

print('hearing...')

stop_listening = r.listen_in_background(m, callback)

for i in range(50):
    time.sleep(5)

stop_listening(wait_for_stop=False)