# TrustStart — run it locally

This is the same code that produced `outputs/evaluation_checkpoint.json` (GPT-4.1 vs Claude Sonnet 4.5 comparison used in the report). Pulled out of the OneDrive project zip and stripped of the `.venv` folder — you'll build a fresh one below.

## 1. Set up a virtual environment

```
python -m venv .venv
```

Windows:
```
.venv\Scripts\activate
```
Mac/Linux:
```
source .venv/bin/activate
```

## 2. Install dependencies

```
pip install -r requirements.txt
```

## Running without API keys (demo mode)

If you skip step 3 below (no `.env`, or empty keys), the app automatically
runs in **demo mode**:

- Paste in one of the original 20 test scenarios (see the report's Test A/B
  section, or `outputs/evaluation_checkpoint.json`) and it returns the real
  recorded GPT-4.1 / Claude Sonnet 4.5 output from that test run.
- Paste in anything else and it falls back to a simple keyword rule engine
  (`models/mock_engine.py`) that mimics the TrustStart prompt's decision
  logic. Each result is clearly labeled "simulated" in the UI so it's never
  mistaken for a real model call.

This is useful for demoing the app's UI and flow at no cost, but it is
**not** a substitute for actually running Test A/B — the graded results
need real API calls. Add your keys (step 3) whenever you want live output.

## 3. Add your API keys (optional — skip for demo mode)

Copy `.env.example` to `.env` and fill in your real keys:

```
cp .env.example .env
```

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

- OpenAI key: https://platform.openai.com/api-keys
- Anthropic key: https://console.anthropic.com/settings/keys

You'll need billing enabled on both — GPT-4.1 and Claude Sonnet each cost a small amount per call (this app calls both on every submission).

## 4. Run the app

```
streamlit run app.py
```

This opens the app in your browser at `http://localhost:8501`. Paste in a remote-start request (there's an example placeholder in the text box) and hit "Evaluate Request" — it calls both models live and shows their decisions side by side.

## Project structure

```
app.py                          Streamlit UI
models/evaluator.py             Calls both models, combines results
models/gpt_client.py            GPT-4.1 call (OpenAI Responses API)
models/claude_client.py         Claude Sonnet call (Anthropic Messages API)
prompts/truststart_prompt.txt   Shared system prompt for both models
outputs/evaluation_checkpoint.json   Logged results from the 20-scenario test run
```

## Note on the model name in claude_client.py

The code currently calls `model="claude-sonnet-4-5"`. If that string ever returns a "model not found" error (Anthropic updates model identifiers over time), check https://docs.claude.com for the current valid model string and swap it in.
