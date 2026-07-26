from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load .env file
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

print(api_key)  # Should print your API key (or at least its beginning)

genai.configure(api_key=api_key)

for model in genai.list_models():
    if "generateContent" in model.supported_generation_methods:
        print(model.name)