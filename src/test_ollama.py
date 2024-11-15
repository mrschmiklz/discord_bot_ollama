import aiohttp
import asyncio
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OllamaModelManager:
    def __init__(self):
        """Initialize the Ollama Model Manager with the base URL from environment variables"""
        self.base_url = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.models_file = 'ollama_models.json'

    async def fetch_models(self):
        """
        Fetch available models from Ollama server
        
        Returns:
            list: List of model information dictionaries
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('models', [])
                    else:
                        print(f"Error: HTTP {response.status}")
                        return []
        except Exception as e:
            print(f"Error connecting to Ollama: {str(e)}")
            return []

    async def save_models_to_json(self):
        """
        Fetch models and save them to a JSON file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            models = await self.fetch_models()
            if models:
                formatted_models = {
                    'total_models': len(models),
                    'models': models,
                    'available_model_names': [model['name'] for model in models]
                }
                
                with open(self.models_file, 'w') as f:
                    json.dump(formatted_models, f, indent=2)
                print(f"Successfully saved {len(models)} models to {self.models_file}")
                return True
            else:
                print("No models found")
                return False
        except Exception as e:
            print(f"Error saving models to JSON: {str(e)}")
            return False

    def read_models_from_json(self):
        """
        Read models from the JSON file
        
        Returns:
            dict: The models data if file exists, None otherwise
        """
        try:
            if os.path.exists(self.models_file):
                with open(self.models_file, 'r') as f:
                    return json.load(f)
            else:
                print(f"Models file {self.models_file} not found")
                return None
        except Exception as e:
            print(f"Error reading models from JSON: {str(e)}")
            return None

async def test_ollama_connection():
    """Test function to check Ollama connection and available models"""
    manager = OllamaModelManager()
    
    print("Testing Ollama connection and fetching models...")
    success = await manager.save_models_to_json()
    
    if success:
        saved_models = manager.read_models_from_json()
        if saved_models:
            print("\nAvailable Models:")
            print("----------------")
            for model in saved_models['models']:
                print(f"Name: {model['name']}")
                print(f"Size: {model.get('size', 'N/A')}")
                print(f"Modified: {model.get('modified', 'N/A')}")
                print("----------------")

if __name__ == "__main__":
    asyncio.run(test_ollama_connection()) 