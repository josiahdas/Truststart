import json
import os
from pathlib import Path

from dotenv import load_dotenv

from models.mock_engine import mock_evaluate


load_dotenv()

API_KEY = os.getenv("ANTHROPIC_API_KEY")

if API_KEY:
    from anthropic import Anthropic
    client = Anthropic(api_key=API_KEY)

PROMPT_PATH = (
    Path(__file__).resolve().parent.parent
    / "prompts"
    / "truststart_prompt.txt"
)


def evaluate_with_claude(request_text: str) -> dict:
    """Evaluate one remote-start request using Claude.

    Falls back to the offline demo engine (models/mock_engine.py) if no
    ANTHROPIC_API_KEY is set, so the app can be demoed without a paid key.
    """

    if not API_KEY:
        return mock_evaluate(request_text, "claude")

    truststart_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        system=truststart_prompt,
        messages=[
            {
                "role": "user",
                "content": request_text,
            }
        ],
    )
    response_text = response.content[0].text.strip()

    if response_text.startswith("```json"):
        response_text = response_text[7:]

    if response_text.endswith("```"):
        response_text = response_text[:-3]

    result = json.loads(response_text.strip())
    result["_source"] = "live"
    return result
