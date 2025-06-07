from fastapi import FastAPI, File, UploadFile, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import speech_recognition as sr
import shutil

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/transcribe/")
async def transcribe(file: UploadFile = File(...)):
    with open("E:/PROJECT/Temp/temp_audio.wav", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    recognizer = sr.Recognizer()
    with sr.AudioFile("E:/PROJECT/Temp/temp_audio.wav") as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            return {"transcription": text}
        except:
            return {"transcription": "Could not transcribe"}

@app.websocket("/ws/transcribe/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    try:
        while True:
            with mic as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = recognizer.listen(source, phrase_time_limit=5)
                try:
                    text = recognizer.recognize_google(audio)
                    await websocket.send_text(text)
                except sr.UnknownValueError:
                    await websocket.send_text("[Unintelligible]")
                except sr.RequestError as e:
                    await websocket.send_text(f"[Error contacting service: {e}]")
    except Exception as e:
        print("WebSocket closed:", e)
        await websocket.close()
