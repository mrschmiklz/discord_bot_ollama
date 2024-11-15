# Discord Ollama Bot

A Discord bot that interfaces with Ollama to provide AI chat capabilities.

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the `.env.example` to `.env` and fill in your details:
   ```bash
   cp .env.example .env
   ```
   - Get your Discord token from the [Discord Developer Portal](https://discord.com/developers/applications)
   - Make sure Ollama is running locally or update the OLLAMA_HOST in .env
   - Set your AI_CHANNEL_ID for the channel where the bot should auto-respond

5. Run the bot:
   ```bash
   python main.py
   ```

## Usage

- The bot will automatically respond to all messages in the configured AI channel
- Use `!chat <your message>` to chat with the AI in other channels
- Use `!reset` to clear the conversation history in the current channel

## Features

- Maintains conversation history per channel
- Automatically expires conversations after 30 minutes of inactivity
- Supports long messages by splitting them into chunks
- Tests Ollama connection on startup
- Saves available models to JSON file

## Requirements

- Python 3.8+
- Discord Bot Token
- Ollama running locally or accessible via network

## Development

To test the Ollama connection separately: