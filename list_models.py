
import google.generativeai as genai
import os

api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("Please set GOOGLE_API_KEY env var")
else:
    genai.configure(api_key=api_key)
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
    except Exception as e:
        print(e)
