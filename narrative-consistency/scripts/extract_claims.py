import csv
import json
import os
from openai import OpenAI

def get_openai_client():
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        return OpenAI(api_key=api_key)
    print("Warning: OPENAI_API_KEY not found in environment.")
    return None

def extract_claims(train_file, output_file):
    """
    Extracts claims from the 'content' column of train.csv using OpenAI API.
    """
    
    if not os.path.exists(train_file):
        print(f"File not found: {train_file}")
        return

    client = get_openai_client()
    if not client:
        return

    claims_map = {}

    with open(train_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        total_rows = len(rows)
        print(f"Processing {total_rows} items...")

        for i, row in enumerate(rows):
            row_id = row['id']
            content = row['content']
            
            prompt = f"""
            You are an expert literary analyst.
            Below is a 'backstory' or description of a character/scene.
            Extract verifiable claims or facts stated in this text.
            These claims will be checked against a novel for consistency.

            Return a JSON object with a key "claims" containing a list of objects.
            Each object must have:
            - "type": "fact", "belief", "capability", "event", or "relationship"
            - "value": concise statement (e.g., "The character is an orphan", "The character hates the sea")
            - "confidence": float 0.0-1.0

            Text:
            {content}
            """

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.0
                )
                
                llm_content = response.choices[0].message.content
                data = json.loads(llm_content)
                claims = data.get("claims", [])
                
                # Add metadata
                for c in claims:
                    c["source"] = "backstory_extraction"
                
                claims_map[row_id] = claims
                
                if i % 10 == 0:
                    print(f"Processed {i}/{total_rows}")

            except Exception as e:
                print(f"Error processing row {row_id}: {e}")
                claims_map[row_id] = []

    # Write to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(claims_map, f, indent=2)
    
    print(f"Extracted claims for {len(claims_map)} items to {output_file}")

if __name__ == "__main__":
    TRAIN_FILE = "data/train.csv"
    OUTPUT_FILE = "output/claims.json"
    extract_claims(TRAIN_FILE, OUTPUT_FILE)
