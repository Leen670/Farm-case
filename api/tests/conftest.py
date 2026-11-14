"""Keep a developer's Gemini key from turning the suite into a live API call."""

import os

os.environ["GEMINI_API_KEY"] = ""
