import csv
import json
import subprocess

MODEL = "mistral"   # pulled via ollama

def ollama_extract(text):
    prompt = f"""
You are an information extraction system.

Extract structured claims from the text below.

Return ONLY a JSON array.
No explanations. No markdown.

Each object must have:
- type: belief | trait | capability | event | relationship
- value: short string
- confidence: number between 0 and 1
- scope: lifelong | temporary

TEXT:
{text}
"""

    result = subprocess.run(
        ["ollama", "run", MODEL],
        input=prompt,
        text=True,
        capture_output=True
    )

    raw = result.stdout.strip()

    # hard guard: extract JSON only
    start = raw.find("[")
    end = raw.rfind("]") + 1
    if start == -1 or end == -1:
        return []

    try:
        return json.loads(raw[start:end])
    except:
        return []


def main():
    claims_db = {}

    with open("data/train.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_id = str(row["id"])
            text = row["content"]

            print(f"Extracting claims for row {row_id}...")
            claims_db[row_id] = ollama_extract(text)

    with open("output/claims.json", "w") as f:
        json.dump(claims_db, f, indent=2)


if __name__ == "__main__":
    main()









