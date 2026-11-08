import json
import re
import time

from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY, MODEL_MAIN

_client = genai.Client(api_key=GEMINI_API_KEY)


def ask_json(prompt, system=None, retries=5):
    """Ask Gemini and return parsed JSON. Retries on errors (429/503)."""
    last_error = None
    for attempt in range(retries):
        try:
            response = _client.models.generate_content(
                model=MODEL_MAIN,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    temperature=0,
                    response_mime_type="application/json",
                ),
            )
            text = (response.text or "").strip()
            text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
            return json.loads(text)
        except Exception as error:
            last_error = error
            wait = 8 * (attempt + 1)
            print(f"  LLM call failed ({type(error).__name__}), retry in {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"LLM failed after {retries} tries: {last_error}")