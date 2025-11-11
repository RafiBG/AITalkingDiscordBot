import whisper
from asyncio import to_thread
import os
import asyncio

RECORDINGS_DIR = "recordings"

class STTProcessor:
    # Handles initialization and execution of the local Whisper Speech-to-Text model.
    def __init__(self):
        self.stt_model = None
        self._load_model()
        
    def _load_model(self):
        print("Loading Whisper 'base' model... This may take a moment.")
        try:
            # Models: tiny, base, small, medium, large
            self.stt_model = whisper.load_model("base", device="cpu") 
            print("Whisper model loaded successfully.")
        except Exception as e:
            print(f"Failed to load Whisper model. Error: {e}")
            self.stt_model = None

    async def transcribe_audio(self, audio_file_path: str) -> str:
        
        # Runs the synchronous Whisper transcription model in a separate thread 
        # and cleans up the audio file afterward.
        # Args: audio_file_path (str): The path to the local WAV file to be transcribed.   
        # Returns:str: The transcribed text.

        if not self.stt_model:
            return "STT Error: Model not loaded."
            
        print(f"[STT] Starting transcription for: {audio_file_path}")
        
        try:
            # Use asyncio.to_thread to run the blocking Whisper code off the main thread.
            result = await to_thread(self.stt_model.transcribe, audio_file_path, fp16=False)
            transcription = result["text"].strip()
        except Exception as e:
            transcription = f"Transcription Error: {e}"
            print(f"STT Failed: {e}")

        # Clean up the audio file after transcription
        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)

        return transcription