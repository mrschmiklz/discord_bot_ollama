import os
import discord
from discord.ext import commands
import aiohttp
from dotenv import load_dotenv
from collections import deque
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Initialize bot with intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

class Conversation:
    def __init__(self, max_history=10):
        self.history = deque(maxlen=max_history)
        self.last_activity = datetime.now()

    def add_message(self, role, content):
        """Add a message to the conversation history"""
        self.history.append({"role": role, "content": content})
        self.last_activity = datetime.now()

    def get_context(self):
        """Get the formatted conversation history"""
        return list(self.history)

    def is_expired(self, timeout_minutes=30):
        """Check if conversation has expired due to inactivity"""
        return datetime.now() - self.last_activity > timedelta(minutes=timeout_minutes)

class OllamaClient:
    def __init__(self):
        self.base_url = os.getenv('OLLAMA_HOST')
        self.model = os.getenv('OLLAMA_MODEL')
        self.conversations = {}

    def get_conversation(self, channel_id):
        """Get or create a conversation for a channel"""
        # Clean up expired conversations
        self._cleanup_expired_conversations()
        
        if channel_id not in self.conversations:
            self.conversations[channel_id] = Conversation()
        return self.conversations[channel_id]

    def _cleanup_expired_conversations(self):
        """Remove expired conversations to free up memory"""
        expired_channels = [
            channel_id for channel_id, conv in self.conversations.items()
            if conv.is_expired()
        ]
        for channel_id in expired_channels:
            del self.conversations[channel_id]

    async def generate_response(self, channel_id, prompt, username):
        """
        Generate a response from Ollama model with conversation context
        
        Args:
            channel_id: The Discord channel ID
            prompt: User's input prompt
            username: Username of the message author
            
        Returns:
            str: Generated response from Ollama
        """
        conversation = self.get_conversation(channel_id)
        
        # Add user message to history
        conversation.add_message("user", f"{username}: {prompt}")

        # Construct the full prompt with conversation history
        context = conversation.get_context()
        formatted_history = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in context[:-1]  # Exclude the last message as it's included in the prompt
        ])
        
        full_prompt = (
            f"Previous conversation:\n{formatted_history}\n\n"
            f"Current message:\n{prompt}\n\n"
            "Please provide a response that takes into account the conversation history."
        )

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": full_prompt,
                        "stream": False
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get('response', 'No response generated')
                        
                        # Add assistant's response to history
                        conversation.add_message("assistant", response_text)
                        
                        return response_text
                    else:
                        return f"Error: HTTP {response.status}"
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}"

# Initialize Ollama client
ollama_client = OllamaClient()

@bot.event
async def on_ready():
    """Event handler for when the bot is ready"""
    print(f'{bot.user} has connected to Discord!')
    ai_channel_id = os.getenv('AI_CHANNEL_ID')
    if not ai_channel_id:
        print("Warning: AI_CHANNEL_ID not set in .env file")
    else:
        print(f"Monitoring channel ID: {ai_channel_id}")

@bot.event
async def on_message(message):
    """Event handler for processing messages"""
    ai_channel_id = int(os.getenv('AI_CHANNEL_ID', 0))
    
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
        
    # Check if the message is in the designated AI channel
    if message.channel.id == ai_channel_id:
        try:
            async with message.channel.typing():
                response = await ollama_client.generate_response(
                    message.channel.id,
                    message.content,
                    message.author.display_name
                )
                
                # Split response if it's too long
                if len(response) > 2000:
                    chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                    for chunk in chunks:
                        await message.reply(chunk)
                else:
                    await message.reply(response)
        except Exception as e:
            await message.channel.send(f"An error occurred: {str(e)}")
    
    await bot.process_commands(message)

@bot.command(name='chat')
async def chat(ctx, *, message: str):
    """Chat command for other channels"""
    try:
        async with ctx.typing():
            response = await ollama_client.generate_response(
                ctx.channel.id,
                message,
                ctx.author.display_name
            )
            
            if len(response) > 2000:
                chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                for chunk in chunks:
                    await ctx.send(chunk)
            else:
                await ctx.send(response)
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command(name='reset')
async def reset_conversation(ctx):
    """Reset the conversation history for the current channel"""
    channel_id = ctx.channel.id
    if channel_id in ollama_client.conversations:
        del ollama_client.conversations[channel_id]
        await ctx.send("Conversation history has been reset.")
    else:
        await ctx.send("No conversation history found for this channel.")

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise ValueError("No Discord token found in .env file")
    bot.run(token) 