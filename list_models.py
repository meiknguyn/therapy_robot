import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key from config/secrets.env
load_dotenv("config/secrets.env")
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise SystemExit("GEMINI_API_KEY not set in config/secrets.env")

genai.configure(api_key=api_key)

print("Models that support generateContent():")
for m in genai.list_models():
    methods = getattr(m, "supported_generation_methods", [])
    if "generateContent" in methods:
        print(" -", m.name)

