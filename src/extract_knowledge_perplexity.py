import os
import requests
from pathlib import Path

# ---------- Paths ----------
TEXT_PATH = Path("data/extracted_text/dsme_refrigeration.txt")
OUTPUT_PATH = Path("kg/raw_facts.json")

# ---------- Load OCR text ----------
text = TEXT_PATH.read_text(encoding="utf-8")

# ---------- Perplexity API ----------
API_KEY = os.getenv("PERPLEXITY_API_KEY")
if not API_KEY:
    raise RuntimeError("PERPLEXITY_API_KEY not set")

URL = "https://api.perplexity.ai/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

SYSTEM_PROMPT = """
You are an information extraction system for ship machinery manuals.

Rules:
1. Extract ONLY facts explicitly stated in the text.
2. Use ONLY the ontology classes and relations provided.
3. Do NOT infer or assume missing components.
4. Output valid JSON only.

Ontology Classes:
- Compressor
- Condenser
- Evaporator
- Valve
- Pipe
- Controller
- Sensor

Relations:
- feeds
- regulates
- returnsTo
- controlledBy
- measuredBy
- triggers

JSON schema:
[
  {
    "subject": "Component_Name",
    "subject_class": "Ontology_Class",
    "predicate": "Relation",
    "object": "Component_Name",
    "object_class": "Ontology_Class",
    "source_page": "Page number if mentioned"
  }
]
"""

USER_PROMPT = f"""
Extract engineering facts from the following OCR text.

Text:
{text[:12000]}
"""

PAYLOAD = {
    "model": "sonar-pro",
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT}
    ],
    "temperature": 0
}

response = requests.post(URL, headers=HEADERS, json=PAYLOAD)
response.raise_for_status()

content = response.json()["choices"][0]["message"]["content"]

OUTPUT_PATH.write_text(content, encoding="utf-8")

print("STEP 3 complete: Raw knowledge facts extracted (Perplexity).")
