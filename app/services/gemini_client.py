# Google Gemini API wrapper for generative AI reasoning and analysis
# Google Gemini API wrapper for generative AI reasoning and analysis

import json
from google import genai
from app.core.config import settings

# initialise the client using the new google-genai SDK
client = genai.Client(api_key=settings.gemini_api_key)

PROMPT_TEMPLATE = """You are a contract risk analyzer. Given the following contract text,
extract clauses and return STRICT JSON only, no markdown, matching this schema:

{{
  "risk_rating": "High" | "Medium" | "Low",
  "summary": "plain-English 2-3 sentence summary of the contract",
  "red_flags": [{{"category": "...", "clause_text": "..."}}],
  "green_flags": [{{"category": "...", "clause_text": "..."}}]
}}

Focus on identifying:
- Interest rates and fee structures
- Hidden charges and late payment penalties
- Prepayment penalties and lock-in periods
- Auto-renewal clauses and cancellation terms

Return ONLY the JSON object. No explanation, no markdown, no extra text.

Contract text:
{contract_text}
"""


def analyze_contract(text: str, max_retries: int = 2) -> dict:
    """
    Send extracted contract text to Gemini API.
    Returns structured JSON with risk_rating, summary, red_flags, green_flags.
    Retries up to max_retries times on failure.
    """
    prompt = PROMPT_TEMPLATE.format(contract_text=text[:30000])  # guard context length

    for attempt in range(max_retries + 1):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )
            # strip markdown code fences if Gemini adds them despite instructions
            cleaned = (
                response.text
                .strip()
                .removeprefix("```json")
                .removeprefix("```")
                .removesuffix("```")
                .strip()
            )
            return json.loads(cleaned)

        except json.JSONDecodeError:
            if attempt == max_retries:
                raise ValueError("Gemini returned invalid JSON after retries.")
            continue

        except Exception as e:
            if attempt == max_retries:
                raise
            continue