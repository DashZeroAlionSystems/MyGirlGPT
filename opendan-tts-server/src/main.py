from fastapi import FastAPI
import schemas
import uvicorn
from starlette.middleware.cors import CORSMiddleware
from functions import *
import base64
import os
import traceback

from bark import SAMPLE_RATE, generate_audio, preload_models
import soundfile as sf
import wave
import numpy as np
import nltk

# fastapi port
server_port = 6006

# Preload model
preload_models()

app = FastAPI(docs_url=None, redoc_url=None)

# Set allowed access domain names
origins = ["*"]  # set to "*" means all.


def concatenate_wavs(wav_files, output_file, silence_duration=0.3):
    wavs = [wave.open(f, 'rb') for f in wav_files]
    sampwidth = wavs[0].getsampwidth()
    framerate = wavs[0].getframerate()
    nchannels = wavs[0].getnchannels()

    samples = [wav.readframes(wav.getnframes()) for wav in wavs]
    total_frames = sum(len(s) for s in samples) + int(silence_duration * framerate * nchannels * sampwidth)

    output = wave.open(output_file, 'wb')
    output.setparams((nchannels, sampwidth, framerate, total_frames, 'NONE', 'Uncompressed'))

    for s in samples:
        output.writeframes(s)
        silence_frame = np.zeros((int(silence_duration * framerate), 2)).astype(np.int16).tobytes()
        for i in range(int(nchannels / 2)):
            output.writeframes(silence_frame)

    output.close()


# Set cross domain parameter transfer
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Set allowed origins sources
    allow_credentials=True,
    allow_methods=["*"],  # Set up HTTP methods that allow cross domain access, such as get, post, put, etc.
    allow_headers=["*"])  # Allowing cross domain headers can be used to identify sources and other functions.


GIRLFRIEND_PRESETS = {
    "sweet": "en_speaker_8",
    "warm": "en_speaker_9",
    "cute": "v2/en_speaker_6",
}


@app.post("/tts_bark/")
async def tts_bark(item: schemas.generate_web):
    time_start = time.time()
    text = item.text
    print(f"{text=}")
    try:
        sentences = nltk.sent_tokenize(text)
        preset = (item.voice_preset or "sweet").lower()
        history_prompt = GIRLFRIEND_PRESETS.get(preset, GIRLFRIEND_PRESETS["sweet"])
        text_temp = item.text_temp if item.text_temp is not None else 0.6
        waveform_temp = item.waveform_temp if item.waveform_temp is not None else 0.6
        idx = 1
        wavs = []
        for s in sentences:
            audio_array = generate_audio(s, history_prompt=history_prompt, text_temp=text_temp, waveform_temp=waveform_temp)
            fname = f"tmp-{idx}.wav"
            sf.write(fname, audio_array, SAMPLE_RATE)
            idx += 1
            wavs.append(fname)
        file_name_pre = f"out-{time.time()}"
        file_name_wav = file_name_pre + ".wav"
        file_name_ogg = file_name_pre + ".ogg"
        concatenate_wavs(wavs, file_name_wav)

        # convert to OGG
        os.system("ffmpeg -i " + file_name_wav + " -c:a libopus -b:a 64k -y " + file_name_ogg)

        with open(file_name_ogg, "rb") as f:
            audio_content = f.read()
        base64_audio = base64.b64encode(audio_content).decode("utf-8")
        res = {"file_base64": base64_audio,
               "audio_text": text,
               "file_name": file_name_ogg,
               }
        print_log(item, res, time_start)
        os.remove(file_name_wav)
        os.remove(file_name_ogg)

        return res
    except Exception as err:
        res = {"code": 9, "msg": "api error", "err": str(err), "traceback": traceback.format_exc()}
        print_log(item, res, time_start)
        return res

if __name__ == '__main__':

    print_env(server_port)
    uvicorn.run(app="main:app", host="0.0.0.0", port=server_port, reload=False)