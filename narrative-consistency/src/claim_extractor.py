from openai import OpenAI
import json

client = OpenAI()

def extract_claims(backstory: str):
    prompt = f"""
Return ONLY a JSON array.

Each object must contain:
- type: belief | trait | capability | event | relationship
- value: short string
- confidence: 0 to 1
- scope: lifelong | temporary

Backstory:
{backstory}
"""

    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )

    raw = response.output_text.strip()

    try:
        return json.loads(raw)
    except:
        return []
