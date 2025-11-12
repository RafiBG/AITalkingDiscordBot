import discord
from discord.ext import commands
import asyncio
import os
import numpy as np
from discord.sinks import WaveSink
from webrtcvad import Vad

# External processors
from stt_processor import STTProcessor
from ai_processor import AIProcessor
from tts_processor import TTSProcessor

#  Config
TOKEN = "Your_token" # Replace with your Discord Bot Token
GUILD_ID = [00000] # Replace with your Discord Server Guild ID/ID
RECORDINGS_DIR = "recordings" # Directory to save audio recordings STT/TTS
os.makedirs(RECORDINGS_DIR, exist_ok=True)

intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True


class VoiceRecorder(commands.Cog):
    def __init__(self, bot, stt_processor, ai_processor, tts_processor):
        self.bot = bot
        self.stt_processor = stt_processor
        self.ai_processor = ai_processor
        self.tts_processor = tts_processor
        self.voice_clients = {}
        self.is_listening = {}
        self.vad = Vad(2)  # Aggressiveness: 0-3

    async def handle_audio_chunk(self, audio_data, vc, channel):
        if not audio_data:
            return

        for user_id, audio in audio_data.items():
            user = vc.guild.get_member(user_id)
            if not user:
                continue

            wav_bytes = audio.file.getvalue()
            data = np.frombuffer(wav_bytes, dtype=np.int16)

            # Check if user is speaking using VAD
            speech_detected = any(
                self.vad.is_speech(chunk.tobytes(), 16000)
                for chunk in np.array_split(data, max(1, len(data)//320))
            )
            if not speech_detected:
                continue

            temp_path = os.path.join(RECORDINGS_DIR, f"chunk_{user_id}.wav")
            with open(temp_path, "wb") as f:
                f.write(wav_bytes)

            print(f"[AUDIO] Received voice chunk from {user.display_name}")

            # STT
            transcribed = await self.stt_processor.transcribe_audio(temp_path)
            if not transcribed.strip():
                continue
            await channel.send(f"**{user.display_name}:** {transcribed}")

            # AI Response
            ai_response = await self.ai_processor.get_ai_response_from_csharp(
                user_id, vc.guild.id, channel.id, transcribed
            )
            if not ai_response.strip():
                continue
            await channel.send(f"**AI:** {ai_response}")

            # TTS Playback
            await self.tts_processor.generate_and_play_audio(vc, ai_response)

    async def listen_loop(self, vc: discord.VoiceClient, channel: discord.TextChannel, guild_id: int):
        self.is_listening[guild_id] = True
        print(f"[LISTEN] Started listening in guild {guild_id}")
        #await channel.send("Listening started!")

        # Proper callback wrapper
        def make_audio_callback(vc, channel):
            def callback(sink, *args):
                asyncio.run_coroutine_threadsafe(
                    self.handle_audio_chunk(sink.audio_data, vc, channel),
                    self.bot.loop
                )
            return callback

        while self.is_listening.get(guild_id, False):
            sink = WaveSink()
            try:
                vc.start_recording(
                    sink,
                    make_audio_callback(vc, channel),
                    None
                )
            except Exception as e:
                print("[ERROR] Could not start recording:", e)
                await asyncio.sleep(1)
                continue

            await asyncio.sleep(6)  # chunk duration

            try:
                vc.stop_recording()
            except Exception:
                pass

            await asyncio.sleep(0.1)

        print(f"[LISTEN] Stopped listening in guild {guild_id}")
        #await channel.send(" Listening stopped. Leaving voice channel.")
        try:
            await vc.disconnect()
        except Exception as e:
            print("[WARN] Disconnect failed:", e)
        if guild_id in self.voice_clients:
            del self.voice_clients[guild_id]

    # /join command
    @commands.slash_command(
        name="join",
        description="Join the voice channel and start the AI conversation.",
        guild_ids=GUILD_ID
    )
    async def join_cmd(self, ctx: discord.ApplicationContext):
        await ctx.defer(ephemeral=True)
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.followup.send("You must be in a voice channel first.", ephemeral=True)

        voice_channel = ctx.author.voice.channel

        try:
            if ctx.guild.id in self.voice_clients and self.voice_clients[ctx.guild.id].is_connected():
                vc = self.voice_clients[ctx.guild.id]
                await vc.move_to(voice_channel)
                msg = f"Moved to **{voice_channel.name}**."
            else:
                vc = await voice_channel.connect()
                self.voice_clients[ctx.guild.id] = vc
                msg = f"Joined **{voice_channel.name}**."

            if not self.is_listening.get(ctx.guild.id, False):
                asyncio.create_task(self.listen_loop(vc, ctx.channel, ctx.guild.id))
                msg += " Started listening for speech."

            await ctx.followup.send(msg, ephemeral=True)
            #await ctx.channel.send(f"**{ctx.author.display_name}** started the AI voice session.")
        except Exception as e:
            await ctx.followup.send(f"Error while joining: `{e}`", ephemeral=True)
            print(f"[ERROR] /join failed: {e}")

    # /leave command
    @commands.slash_command(
        name="leave",
        description="Stop listening and leave the voice channel.",
        guild_ids=GUILD_ID
    )
    async def leave_cmd(self, ctx: discord.ApplicationContext):
        guild_id = ctx.guild.id
        self.is_listening[guild_id] = False

        vc = self.voice_clients.get(guild_id)
        if vc and vc.is_connected():
            try:
                await vc.disconnect()
            except Exception:
                pass
        await ctx.respond("Stopped listening and left the voice channel.", ephemeral=True)


class BotClient(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

        # Initialize processors
        self.stt_processor = STTProcessor()
        self.ai_processor = AIProcessor(self)
        self.tts_processor = TTSProcessor()

        self.add_cog(VoiceRecorder(self, self.stt_processor, self.ai_processor, self.tts_processor))

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        print("Bot is ready.")


# Bot runs here
if __name__ == "__main__":
    bot = BotClient()
    bot.run(TOKEN)
