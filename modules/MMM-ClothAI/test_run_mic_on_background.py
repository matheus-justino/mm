import threading, time, asyncio, random

target1 = ''
target2 = ''

def run_command():
    print('rodando comando!')

async def get_microphone():
    global target2

    while True:
        print('gravando...')
        await asyncio.sleep(5)
        target2 = 'a'*random.randint(0, 10)
        print('salvo.')

async def get_transcription():
    global target2

    while True:
        print('analisando...')
        await asyncio.sleep(5)
        print(f"{len(target2)}")

        if len(target2) > 5:
            print('detectado!')
            run_command()

async def run_mic_detection():
    tasks = [get_transcription(), get_microphone()]

    await asyncio.gather(*tasks)

def background_mic():
    # asyncio.run(run_mic_detection())
    loop = asyncio.get_event_loop()
    task = asyncio.ensure_future(run_mic_detection())
    loop.run_forever()

background_mic()