# 🗣️ AITalkingDiscordBot (Python Voice Client)

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Discord.py](https://img.shields.io/badge/Library-discord.py-blueviolet.svg)](https://discordpy.readthedocs.io/en/latest/)

This is the dedicated voice client for the **AIChatDiscordBotWeb** (C# repository). It handles all real-time audio processing, allowing users to talk directly to the AI in a Discord voice channel.

---

## 🧠 Architecture: How it Works

This bot serves as the **ears and mouth** for primary C# bot **AIChatDiscordBotWeb** (the "brain").

1.  **Speech-to-Text (STT):** The bot listens in the voice channel, records user speech, and converts it to text.
2.  **AI Processing:** The text is sent to the **AIChatDiscordBotWeb** (C#) for AI response generation.
3.  **Text-to-Speech (TTS):** The C# bot's response is sent back here. This Python client uses **Piper TTS** to generate the voice audio.
4.  **Output:** The generated audio is outputted back into the Discord voice channel.

**IMPORTANT:** This bot is a client only and **requires** the [AIChatDiscordBotWeb](https://github.com/RafiBG/AIChatDiscordBotWeb) to be running simultaneously.

---

## 🛠️ Prerequisites

Before running the bot, you must install and configure the following external tools:

### 1. FFmpeg (Audio Processing)
FFmpeg is essential for handling audio streams and must be installed and accessible in your system **PATH**.
* [**Video Guide: How to Install FFmpeg**](https://www.youtube.com/watch?v=eRZRXpzZfM4)

### 2. Piper TTS (Voice Generation)
Piper is a fast, local, and high-quality Text-to-Speech engine.
* Install `Piper.exe` and download your desired voice model (`.onnx` file).
* [**Video Guide: How to Install Piper TTS**](https://www.youtube.com/watch?v=GGvdq3giiTQ)

---

## ⚙️ Installation & Setup

### 1. Discord Developer Portal
1.  Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2.  Create a new application and go to the **Bot** tab.
3.  **Privileged Gateway Intents:** Scroll down and enable the intents shown below:
    ![privilage](https://github.com/user-attachments/assets/f6a7ae67-acf6-4d11-a479-7b55df3fab02)
4.  **Installation:** Ensure the bot has the following permissions enabled:
    <img src="https://github.com/user-attachments/assets/82fd8312-0e45-4ab2-b4c0-003f367a1028" />
5.  Copy your **Bot Token**. You will need it.

### 1. Install Python Dependencies
```
pip install -r requirements.txt
```
### 2. Configure main.py
```
# Replace with your specific Discord Bot Token for this application
TOKEN = "second-discord-bot-token" 

# Replace with the Discord Server (Guild) ID where the bot will operate
GUILD_ID = [server-id]
```
### 3. Configure tts_processor.py
```
# Replace with the exact name of your downloaded Piper voice model (.onnx file)
PIPER_MODEL_NAME = "jarvis-high.onnx"
```
### 4. Run the bot
```
main.py or in console "python main.py"

# Replace with the full, absolute path to the Piper.exe executable
PIPER_EXECUTABLE_PATH = "C:/Downloads/PiperTTS/piper.exe"
```
