import json
import os
from pathlib import Path

from dotenv import load_dotenv

from models.mock_engine import mock_evaluate


load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

if API_KEY:
    from openai import OpenAI
    client = OpenAI(api_key=API_KEY)

PROMPT_PATH = (
    Path(__file__).resolve().parent.parent
    / "prompts"
    / "truststart_prompt.txt"
)


def evaluate_with_gpt(request_text: str) -> dict:
    """Evaluate one remote-start request using GPT.

    Falls back to the offline demo engine (models/mock_engine.py) if no
    OPENAI_API_KEY is set, so the app can be demoed without a paid key.
    """

    if not API_KEY:
        return mock_evaluate(request_text, "gpt")

    truststart_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    response = client.responses.create(
        model="gpt-4.1",
        instructions=truststart_prompt,
        input=request_text,
    )

    result = json.loads(response.output_text)
    result["_source"] = "live"
    return result
