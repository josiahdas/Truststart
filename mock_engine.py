"""
Offline demo engine for TrustStart.

Used automatically by gpt_client.py / claude_client.py when the matching
API key is missing, so the app can be demoed without any cost or network
access.

Two paths:
1. If the pasted request text matches one of the 20 original logged test
   scenarios closely enough, return the REAL recorded GPT-4.1 / Claude
   Sonnet 4.5 output from outputs/evaluation_checkpoint.json.
2. Otherwise, fall back to a simple keyword-based rule engine that mimics
   the TrustStart prompt's decision logic. This is NOT a real model call —
   every result it returns is tagged "simulated" so it's never confused
   with a real GPT/Claude response.
"""

import json
import re
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / "_demo_data.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    _KNOWN_SCENARIOS = json.load(f)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _find_known_match(request_text: str):
    """Exact-ish match against the 20 logged scenarios."""
    norm_input = _normalize(request_text)
    for scenario in _KNOWN_SCENARIOS:
        if _normalize(scenario["requestText"]) == norm_input:
            return scenario
    return None


def _rule_based_decision(text: str) -> dict:
    """
    Lightweight keyword simulation of the TrustStart evaluation policy.
    This intentionally mirrors the criteria in prompts/truststart_prompt.txt
    but is a simple heuristic, not a language model — treat its output as
    illustrative only.
    """
    t = text.lower()

    def has_any(*phrases):
        return any(p in t for p in phrases)

    missing_evidence, risk_flags, controls = [], [], []

    # --- BLOCK: hard safety / security failures ---
    estop_mentioned = "emergency stop" in t or "e-stop" in t or "estop" in t
    estop_engaged = estop_mentioned and "engaged" in t and "released" not in t
    if estop_engaged:
        return _result("BLOCK",
            "Emergency stop is engaged, which is an automatic blocking condition "
            "under the TrustStart policy. Remote start cannot proceed until the "
            "emergency stop is physically cleared on site.",
            [], ["Emergency stop engaged"],
            ["Require local personnel to clear the emergency stop before resubmitting."])

    account_expired = ("account" in t and "expired" in t)
    command_expired = (("command" in t or "expiration" in t) and "expired" in t)
    if account_expired or command_expired:
        return _result("BLOCK",
            "An expired account or expired command window is treated as an automatic "
            "denial condition, regardless of other evidence present.",
            [], ["Expired credential or expired command window"],
            ["Reissue a valid command / renew the account before resubmitting."])

    if has_any("account is disabled", "account status: disabled", "disabled account"):
        return _result("BLOCK",
            "A disabled requester account is a critical access-control failure and "
            "blocks the request outright.",
            [], ["Disabled account submitted a remote-start request"],
            ["Investigate how a disabled account issued this request before any further action."])

    # --- ESCALATE: unusual / high-risk characteristics ---
    if has_any("vendor", "firmware", "third-party", "third party", "override",
               "overriding", "overrides a", "unusual", "calibration"):
        return _result("ESCALATE",
            "The request involves elevated-risk activity (vendor/firmware access, an "
            "override of a prior decision, or similarly unusual circumstances) that "
            "the policy treats as requiring human review before approval, even though "
            "the basic evidence checklist is otherwise satisfied.",
            [], ["Unusual or high-risk activity requiring supervisory review"],
            ["Route to a human reviewer before approving or denying."])

    # --- NEEDS_EVIDENCE: fixable gaps ---
    if has_any("no one has confirmed", "not confirmed", "no local confirmation",
               "local confirmation: no", "confirmation: unknown", "unknown local confirmation"):
        missing_evidence.append("Local personnel confirmation")
        risk_flags.append("Local confirmation missing or unknown")

    if has_any("no work order", "work order: none", "missing work order",
               "none provided", "work order: missing", "work order: expired"):
        missing_evidence.append("Valid work order")
        risk_flags.append("Work order missing or expired")

    if has_any("audit logging: disabled", "audit log disabled", "logging is disabled"):
        missing_evidence.append("Audit logging enabled")
        risk_flags.append("Audit logging disabled")

    if missing_evidence:
        controls.append("Provide the missing evidence above before resubmitting.")
        return _result("NEEDS_EVIDENCE",
            "Most required evidence is present, but the request is missing information "
            "needed to safely approve it. This is resolvable rather than an automatic denial.",
            missing_evidence, risk_flags, controls)

    # --- APPROVE: default when nothing above triggered ---
    return _result("APPROVE",
        "The request appears to satisfy the standard evidence checklist (zone identified, "
        "justification provided, local confirmation, safe state, valid command window, and "
        "audit logging) with no automatic blocking or escalation conditions detected.",
        [], [], [])


def _result(decision, rationale, missing_evidence, risk_flags, controls):
    return {
        "decision": decision,
        "rationale": rationale,
        "missing_evidence": missing_evidence,
        "risk_flags": risk_flags,
        "recommended_controls": controls,
    }


def mock_evaluate(request_text: str, model_label: str) -> dict:
    """
    model_label is 'gpt' or 'claude' — used only to pull the right side of
    a known-scenario record. Returns a plain dict shaped like the real
    parsed JSON response (decision/rationale/missing_evidence/risk_flags/
    recommended_controls), plus a "_source" field noting where it came from.
    """
    match = _find_known_match(request_text)
    if match:
        result = dict(match[model_label])
        result.pop("correct", None)
        result["decision"] = result["decision"]
        result["_source"] = "recorded"
        return result

    result = _rule_based_decision(request_text)
    result["_source"] = "simulated"
    return result
