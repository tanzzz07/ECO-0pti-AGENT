import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the API key
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

try:
    print("Fetching models available to your API key...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Model Name: {m.name}, Supported: {m.supported_generation_methods}")
except Exception as e:
    print(f"An error occurred: {e}")