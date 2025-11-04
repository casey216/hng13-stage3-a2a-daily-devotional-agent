# app/agents/generator.py
import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

token = "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"
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1"

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)


def _extract_json_from_text(text: str):
    """Try to find a JSON object in model output. Return parsed JSON or raise."""
    # Try direct parse first
    try:
        return json.loads(text)
    except Exception:
        pass

    # Try finding first {...} block
    m = re.search(r"(\{.*\})", text, re.DOTALL)
    if m:
        candidate = m.group(1)
        try:
            return json.loads(candidate)
        except Exception:
            # try to fix trailing commas etc - minimal cleanup
            candidate_clean = re.sub(r",\s*}", "}", candidate)
            candidate_clean = re.sub(r",\s*\]", "]", candidate_clean)
            return json.loads(candidate_clean)
    raise ValueError("No valid JSON object found in model output")

def generate_structured_devotional(reference: str, verse_text: str, tone: str = "encouraging"):
    """
    Ask the LLM to return a JSON object with fields:
      title, scripture_ref, scripture_text, reflection, application, prayer
    The model is instructed to reply with JSON only. Parsing is resilient.
    """
    prompt = f"""
You are a warm, pastoral Christian devotional writer.

Given the scripture reference and verse text below, produce a JSON object (no extra text)
with exactly these keys:
 - title (string, 5-10 words)
 - scripture_ref (string)
 - scripture_text (string)
 - reflection (string, 3-5 sentences)
 - application (string, 1-3 short bullet points joined by ' ; ')
 - prayer (string, 1 short paragraph)

Tone: {tone}

INPUT:
REFERENCE: {reference}
VERSE: {verse_text}

Respond with valid JSON only.
"""
    try:
        resp = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
                ],
                temperature=1,
                top_p=1,
                model=model
        )
        
        text = resp.choices[0].message.content.strip()
        data = _extract_json_from_text(text)

        # Minimal validation
        required = ['title', 'scripture_ref', 'scripture_text', 'reflection', 'application', 'prayer']
        for k in required:
            if k not in data:
                raise ValueError(f"Missing key '{k}' in model output")
        return {
            "title": str(data["title"]).strip(),
            "scripture_ref": str(data["scripture_ref"]).strip(),
            "scripture_text": str(data["scripture_text"]).strip(),
            "reflection": str(data["reflection"]).strip(),
            "application": str(data["application"]).strip(),
            "prayer": str(data["prayer"]).strip(),
        }
    except Exception as e:
        # bubble up; caller may fallback
        raise RuntimeError(f"LLM generation failed: {e}")
