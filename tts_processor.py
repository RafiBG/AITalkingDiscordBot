import asyncio
import os
import subprocess
from asyncio import to_thread
from discord import PCMVolumeTransformer
import discord
from discord.opus import Encoder
from discord.sinks import WaveSink

# Configuration for Piper  The Piper.exe runs on CPU only.
PIPER_MODEL_NAME = "en_GB-northern_english_male-medium.onnx" # Replace with your desired Piper model name
PIPER_EXECUTABLE_PATH = "C:/Downloads/PiperTTS/piper.exe"  # Replace this path to your Piper executable location
RECORDINGS_DIR = "recordings"

# Calculate the ABSOLUTE path for the recordings directory
# This ensures the output path is always clear
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ABSOLUTE_RECORDINGS_DIR = os.path.join(BASE_DIR, RECORDINGS_DIR)

PIPER_DIRECTORY = os.path.dirname(PIPER_EXECUTABLE_PATH)


class TTSProcessor:
    #Handles local Piper Text-to-Speech generation via subprocess.
    def __init__(self):
        print(f"TTSProcessor initialized. Using Piper model: {PIPER_MODEL_NAME}")
        
    def _generate_audio_sync(self, text: str, output_file_path: str):
        # Synchronously runs the Piper executable to generate a WAV file.
        # This runs in a separate thread.

        if not text:
            print("Error: TTS text is empty.")
            return False

        try:
            output_dir = os.path.dirname(output_file_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                print(f"[TTS] Created recording directory: {output_dir}")
                
            # Command structure: piper -m <model> -f <path>
            command = [
                PIPER_EXECUTABLE_PATH,
                "-m", PIPER_MODEL_NAME,
                "-f", output_file_path,
                "--disable_decoder_management"
            ]

            # subprocess.run is to execute the command synchronously
            process = subprocess.run(
                command, 
                input=text.encode('utf-8'), 
                capture_output=True, 
                check=True,
                cwd=PIPER_DIRECTORY
            )
            
            if os.path.exists(output_file_path):
                print(f"[TTS] Successfully generated audio at: {output_file_path}")
                return True
            else:
                print(f"[TTS] Error: Piper ran, but output file not found at: {output_file_path}. Stderr: {process.stderr.decode()}")
                return False

        except subprocess.CalledProcessError as e:
            print(f"[TTS] Piper failed (Code {e.returncode}): {e.stderr.decode()}")
            return False
        except FileNotFoundError:
            print(f"[TTS] Error: Piper executable not found at '{PIPER_EXECUTABLE_PATH}'.")
            return False
        except Exception as e:
            print(f"[TTS] An unexpected error occurred: {e}")
            return False

    async def generate_and_play_audio(self, vc: discord.VoiceClient, text: str) -> str:
        # Generates audio using Piper in a thread and plays it in the voice channel.
        output_filename = f"ai_response_{vc.guild.id}_{vc.user.id}.wav"
        
        # Piper will now receive the full unambiguous path, e.g., C:\...\VoiceBot\recordings\file.wav
        output_filepath = os.path.join(ABSOLUTE_RECORDINGS_DIR, output_filename)

        os.makedirs(ABSOLUTE_RECORDINGS_DIR, exist_ok=True)
        
        # Remove previous file if it exists
        if os.path.exists(output_filepath):
            os.remove(output_filepath)
        
        # Run the synchronous
        success = await to_thread(self._generate_audio_sync, text, output_filepath)

        if success:
            try:
                source = PCMVolumeTransformer(discord.FFmpegPCMAudio(output_filepath))
                
                # Check if the bot is already playing audio
                if vc.is_playing():
                    vc.stop() 

                vc.play(source, after=lambda e: print(f'Player error: {e}') if e else os.remove(output_filepath))
                
                # Wait until the audio is done playing
                while vc.is_playing():
                    await asyncio.sleep(0.1)

                return output_filepath

            except Exception as e:
                print(f"[TTS Playback Error]: {e}")
                # Ensure the file is deleted on playback failure
                if os.path.exists(output_filepath):
                    os.remove(output_filepath)
                return None
        
        return None # Failed to generate audio