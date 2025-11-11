import requests
from asyncio import to_thread

# Configuration

# C# API Endpoint that receives the text and returns the AI response
CSHARP_AI_ENDPOINT = "https://localhost:7033/api/process_transcription" 
# Replace 7033 with your actual C# application port.

class AIProcessor:
    #Handles communication with the external C# AI service.
    
    def __init__(self, bot):
        self.bot = bot
        print(f"AIProcessor initialized. Targeting C# endpoint: {CSHARP_AI_ENDPOINT}")

    async def get_ai_response_from_csharp(self, user_id: int, guild_id: int, channel_id: int, transcribed_text: str) -> str:
        # Sends the transcribed text to the C# bot and waits for the AI response.
        # This method acts as a client to the C# server.
        
        payload = {
            "userId": str(user_id),
            "guildId": str(guild_id),
            "channelId": str(channel_id),
            "transcription": transcribed_text
        }
        
        print(f"Sending transcription to C# for AI processing...")
        
        try:
            # requests.post is synchronous, so we run it using asyncio.to_thread
            response = await to_thread(requests.post, CSHARP_AI_ENDPOINT, json=payload, timeout=30, verify=False)
            
            # Check for successful HTTP response (200 OK)
            if response.status_code == 200:
                data = response.json()
                # Expecting the C# application to return a JSON with an 'aiResponse' field
                ai_response = data.get("aiResponse", "C# returned an empty response.")
                print("Received AI response from C# successfully.")
                return ai_response
            else:
                print(f"C# API reported error. Status: {response.status_code}, Body: {response.text}")
                return f"Error connecting to AI: C# server returned status {response.status_code}."
                
        except requests.exceptions.Timeout:
            print(" C# API request timed out (30 seconds).")
            return "Error: AI processing timed out."
        except requests.exceptions.RequestException as e:
            print(f"Network Error connecting to C# API: {e}")
            return f"Error: Could not reach C# server at {CSHARP_AI_ENDPOINT}."