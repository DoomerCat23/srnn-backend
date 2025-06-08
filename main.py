from fastapi import FastAPI, File, UploadFile, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import speech_recognition as sr
import shutil
import os
from pydub import AudioSegment

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend domain before deploying
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/transcribe/")
async def transcribe(file: UploadFile = File(...)):
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)

    # Get file extension
    input_ext = file.filename.split(".")[-1].lower()
    input_path = os.path.join(temp_dir, f"input.{input_ext}")
    wav_path = os.path.join(temp_dir, "converted.wav")

    # Save the uploaded file
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Convert to WAV format
    try:
        if input_ext != "wav":
            audio = AudioSegment.from_file(input_path)
            audio.export(wav_path, format="wav")
        else:
            wav_path = input_path
    except Exception as e:
        return {"transcription": f"Error converting audio: {str(e)}"}

    # Transcribe WAV audio
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return {"transcription": text}
    except Exception as e:
        return {"transcription": f"Could not transcribe: {str(e)}"}

@app.websocket("/ws/transcribe/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Live transcription is not supported in the deployed version.")
    await websocket.close()
