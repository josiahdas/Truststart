import os

import streamlit as st
from dotenv import load_dotenv

from models.evaluator import evaluate_request

load_dotenv()

DEMO_MODE = not (os.getenv("OPENAI_API_KEY") and os.getenv("ANTHROPIC_API_KEY"))


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="TrustStart",
    page_icon="🛡️",
    layout="wide",
)


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def show_decision(decision: str) -> None:
    normalized_decision = decision.strip().upper()

    labels = {
        "APPROVE": "Approve",
        "NEEDS_EVIDENCE": "Needs Evidence",
        "ESCALATE": "Escalate",
        "BLOCK": "Block",
    }

    display = labels.get(normalized_decision, normalized_decision.title())

    if normalized_decision == "APPROVE":
        st.success(f"Decision: {display}")
    elif normalized_decision == "NEEDS_EVIDENCE":
        st.warning(f"Decision: {display}")
    elif normalized_decision == "ESCALATE":
        st.info(f"Decision: {display}")
    elif normalized_decision == "BLOCK":
        st.error(f"Decision: {display}")
    else:
        st.error(f"Decision: {display}")

def show_list(items: list, empty_message: str = "None") -> None:
    if not items:
        st.write(empty_message)
        return

    for item in items:
        st.markdown(f"- {item}")


def show_model_results(model_name: str, result: dict) -> None:
    with st.container(border=True):

        st.header(model_name)

        source = result.get("_source")
        if source == "recorded":
            st.caption("Matched one of the 20 logged test scenarios — showing the real recorded output.")
        elif source == "simulated":
            st.caption("Demo mode: simulated with a keyword rule engine, not a live model call.")

        show_decision(result.get("decision", "UNKNOWN"))

        st.subheader("Rationale")
        st.write(result.get("rationale", "No rationale returned."))

        st.subheader("Missing Evidence")
        show_list(result.get("missing_evidence", []))

        st.subheader("Risk Flags")
        show_list(result.get("risk_flags", []))

        st.subheader("Recommended Controls")
        show_list(result.get("recommended_controls", []))


# --------------------------------------------------
# Header
# --------------------------------------------------

if DEMO_MODE:
    st.info(
        "Running in demo mode — no API keys detected in .env. Pasting one of the "
        "20 original test scenarios returns the real recorded GPT-4.1 / Claude "
        "Sonnet 4.5 output; anything else is simulated with a simple rule engine, "
        "not a live model call. Add OPENAI_API_KEY and ANTHROPIC_API_KEY to .env "
        "for live results."
    )

st.title("🛡️ TrustStart")

st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

st.subheader("AI-Assisted Security Review for Remote Start Requests")

st.markdown(
    """
TrustStart reviews industrial remote-start requests to identify missing
evidence, highlight potential security and safety risks, and recommend
additional controls before a request is approved.
"""
)


# --------------------------------------------------
# Instructions
# --------------------------------------------------

with st.expander("What information should I include?"):

    st.markdown(
        """
Include as much of the following information as possible:

- Target zone
- Reason for remote start
- Local confirmation
- Safety state verification
- Command expiration
- Audit logging
- Work order or maintenance ticket
"""
    )


# --------------------------------------------------
# User Input
# --------------------------------------------------

request = st.text_area(
    "Enter a remote start request:",
    height=250,
    placeholder=(
        "Paste your remote-start request here...\n\n"
        "Target zone: Zone 4\n"
        "Reason: Sensor verification\n"
        "Local confirmation: Confirmed by onsite technician\n"
        "Safety state verified: Yes\n"
        "Command expiration: 5 minutes\n"
        "Audit logging: Enabled"
    ),
)


# --------------------------------------------------
# Evaluation
# --------------------------------------------------

if st.button("Evaluate Request"):

    if not request.strip():
        st.warning("Please enter a remote start request.")

    else:

        try:

            with st.spinner("Performing security review..."):
                results = evaluate_request(request)

            st.divider()

            st.header("🛡️ Model Comparison")

            col1, col2 = st.columns(2, gap="large")

            with col1:
                show_model_results(
                    "GPT-4.1",
                    results["gpt"],
                )

            with col2:
                show_model_results(
                    "Claude Sonnet 4.5",
                    results["claude"],
                )

        except Exception as error:
            st.error("The request could not be evaluated.")
            st.exception(error)


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    """
TrustStart MVP | AI-Assisted Security Review for Remote-Start Requests

GPT-4.1 vs. Claude Sonnet 4.5 | Kennesaw State University
"""
)