
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MODEL_MAIN = "gemini-3.5-flash-lite"
MODEL_CHEAP = "gemini-3.5-flash-lite"

