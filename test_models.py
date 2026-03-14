import google.generativeai as genai
import sys

def list_models(api_key):
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        print("AVAILABLE MODELS:")
        for m in models:
            print(f"- {m}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        list_models(sys.argv[1])
    else:
        print("Please provide an API key as an argument.")
