import json
import os
import pickle
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI

# Input/Output
INPUT_FILE = "output/constraints.jsonl"
OUTPUT_FILE = "output/constraints_with_embeddings.pkl"
MAX_WORKERS = 20

def get_openai_client():
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        return OpenAI(api_key=api_key)
    print("Warning: OPENAI_API_KEY not found.")
    return None

def get_embedding(text, client, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    try:
        return client.embeddings.create(input=[text], model=model).data[0].embedding
    except Exception as e:
        print(f"Error embedding text: {e}")
        return []

def process_line(line, client):
    try:
        data = json.loads(line)
        constraint = data.get("constraints", {})
        text_to_embed = f"{constraint.get('entity', '')} {constraint.get('value', '')}"
        embedding = get_embedding(text_to_embed, client)
        if embedding:
            return {
                "constraint": constraint,
                "embedding": embedding,
                "book_name": constraint.get("book_name")
            }
    except Exception as e:
        pass
    return None

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"File not found: {INPUT_FILE}")
        return

    client = get_openai_client()
    if not client:
        return

    print("Reading lines from constraints.jsonl...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Generating embeddings for {len(lines)} constraints using {MAX_WORKERS} workers...")
    
    constraints_data = []
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_line, line, client) for line in lines]
        for i, future in enumerate(as_completed(futures)):
            result = future.result()
            if result:
                constraints_data.append(result)
            
            if (i + 1) % 100 == 0:
                print(f"Processed {i + 1}/{len(lines)}...")

    # Save to pickle
    with open(OUTPUT_FILE, 'wb') as f:
        pickle.dump(constraints_data, f)
        
    print(f"Saved {len(constraints_data)} embedded constraints to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
