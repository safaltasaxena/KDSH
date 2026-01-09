import csv
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.constraint_extractor import extract_constraints

INPUT_FILE = "data/chunks.csv"
OUTPUT_FILE = "output/constraints.jsonl"
MAX_WORKERS = 25 # Adjust based on rate limits

def process_chunk(row):
    chunk_id = int(row['chunk_id'])
    book_name = row['book_name']
    text = row['text']
    try:
        extracted_list = extract_constraints(text, chunk_id, book_name)
        return chunk_id, extracted_list
    except Exception as e:
        print(f"Error processing chunk {chunk_id}: {e}")
        return chunk_id, []

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Input file not found: {INPUT_FILE}")
        return

    # Load existing chunk_ids to skip
    processed_chunk_ids = set()
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    processed_chunk_ids.add(data["constraints"]["chunk_id"])
                except:
                    continue
    
    print(f"Found {len(processed_chunk_ids)} already processed chunks.")

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        all_rows = [row for row in reader if int(row['chunk_id']) not in processed_chunk_ids]

    print(f"Remaining chunks to process: {len(all_rows)}")

    with open(OUTPUT_FILE, 'a', encoding='utf-8') as fout:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_chunk = {executor.submit(process_chunk, row): row for row in all_rows}
            
            for i, future in enumerate(as_completed(future_to_chunk)):
                chunk_id, extracted_list = future.result()
                
                for constraint in extracted_list:
                    output_obj = {
                        "constraints": constraint,
                        "diff": 1
                    }
                    fout.write(json.dumps(output_obj) + "\n")
                
                fout.flush()
                
                if (i + 1) % 10 == 0:
                    print(f"Completed {i + 1}/{len(all_rows)} chunks...")

if __name__ == "__main__":
    main()
