import os
from src.bot import bot
from dotenv import load_dotenv
from src.test_ollama import test_ollama_connection
import asyncio

async def startup_sequence():
    """Run startup checks and start the bot"""
    # Load environment variables
    load_dotenv()
    
    # Test Ollama connection before starting bot
    print("Testing Ollama connection...")
    await test_ollama_connection()
    
    # Get Discord token
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise ValueError("No Discord token found in .env file")
    
    print("\nStarting Discord bot...")
    try:
        await bot.start(token)
    except Exception as e:
        print(f"Error starting bot: {str(e)}")

if __name__ == "__main__":
    asyncio.run(startup_sequence()) 