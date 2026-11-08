print("Test started", flush=True)

from google import genai
from google.genai import types
from src.config import GEMINI_API_KEY, MODEL_MAIN

client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options=types.HttpOptions(
        timeout=15000,
        retry_options=types.HttpRetryOptions(attempts=1),
    ),
)

print("Sending request...", flush=True)

try:
    response = client.models.generate_content(
        model=MODEL_MAIN,
        contents="Say hello in one short sentence.",
    )
    print("Gemini says:", response.text, flush=True)
except Exception as e:
    print("ERROR:", type(e).__name__, str(e), flush=True)
finally:
    client.close()