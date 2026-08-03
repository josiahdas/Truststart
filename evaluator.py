from models.gpt_client import evaluate_with_gpt
from models.claude_client import evaluate_with_claude


def evaluate_request(request_text: str) -> dict:
    """
    Send the same TrustStart request to GPT and Claude
    and return both structured results.
    """

    gpt_result = evaluate_with_gpt(request_text)
    claude_result = evaluate_with_claude(request_text)

    return {
        "gpt": gpt_result,
        "claude": claude_result,
    }