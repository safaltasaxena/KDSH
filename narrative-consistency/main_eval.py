import json
import csv
import pickle
import numpy as np
import os
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
from src.contradiction_logic import contradiction_score
from src.decision import aggregate_scores, decide_label

THRESHOLDS = [0.3, 0.4, 0.5, 0.6, 0.7] # Although we will likely get binary outputs from LLM

# ---------- LOAD RESOURCES ----------
print("Loading constraints & embeddings...")
CONSTRAINTS_FILE = "output/constraints_with_embeddings.pkl"
try:
    with open(CONSTRAINTS_FILE, "rb") as f:
        constraints_db = pickle.load(f)
except FileNotFoundError:
    print(f"Error: {CONSTRAINTS_FILE} not found. Run scripts/embed_constraints.py first.")
    constraints_db = []

print("Loading claims...")
with open("output/claims.json", "r") as f:
    claims_map = json.load(f)

# Initialize OpenAI for query embedding
def get_openai_client():
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        return OpenAI(api_key=api_key)
    return None

client = get_openai_client()

def get_embedding(text):
    if not client: return []
    try:
        return client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding
    except Exception:
        return []

def retrieve_top_k(claim_text, book_name, k=5):
    """
    Find top k constraints from the same book similar to claim_text.
    """
    if not client or not constraints_db:
        return []

    # Filter candidates by book
    candidates = [c for c in constraints_db if c.get("book_name") == book_name]
    if not candidates:
        return []

    # Get claim embedding
    claim_vec = get_embedding(claim_text)
    if not claim_vec:
        return []

    # Calculate similarity
    # Stack vectors
    candidate_vecs = np.array([c["embedding"] for c in candidates])
    claim_vec = np.array([claim_vec])
    
    # Cosine similarity
    sims = cosine_similarity(claim_vec, candidate_vecs)[0]
    
    # Top indices
    top_indices = sims.argsort()[-k:][::-1]
    
    return [candidates[i]["constraint"] for i in top_indices]

from concurrent.futures import ThreadPoolExecutor, as_completed

CACHE_FILE = "output/eval_scores.json"

def process_row(row, claims_map):
    row_id = str(row["id"])
    book_name = row["book_name"]
    ground_truth = row["label"]
    char_name = row.get('char', '')
    
    claims = claims_map.get(row_id, [])
    scores = []
    
    for claim in claims:
        # Prepend character name for better similarity matching with constraints
        claim_text = f"{char_name} {claim.get('value', '')}"
        top_constraints = retrieve_top_k(claim_text, book_name, k=10)
        
        for constraint in top_constraints:
            try:
                s = contradiction_score(claim, constraint)
                if s > 0:
                    scores.append(s)
            except Exception as e:
                # If we hit rate limit or other error, we don't want to save 0.0 prematurely
                # unless we want to catch it specifically. For now, just skip.
                print(f"Error checking contradiction for {row_id}: {e}")
                pass

    final_score = 0.0
    if scores:
        final_score = aggregate_scores(scores, method="weighted")
        
    return {
        "id": row_id,
        "score": final_score,
        "label": ground_truth
    }

def evaluate(test_file):
    with open(test_file, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Load existing results
    cached_results = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                cached_results = {row["id"]: row for row in json.load(f)}
            print(f"Loaded {len(cached_results)} cached scores.")
        except:
            pass

    print(f"Evaluating {len(rows)} rows with RAG & Parallelization...")
    
    results = []
    rows_to_process = [r for r in rows if str(r["id"]) not in cached_results]
    
    # Add already processed ones
    for rid in cached_results:
        results.append(cached_results[rid])

    if rows_to_process:
        MAX_EVAL_WORKERS = 10 
        with ThreadPoolExecutor(max_workers=MAX_EVAL_WORKERS) as executor:
            future_to_row = {executor.submit(process_row, row, claims_map): row for row in rows_to_process}
            
            for i, future in enumerate(as_completed(future_to_row)):
                try:
                    res = future.result()
                    results.append(res)
                    # Save progress every time a row is finished to be safe
                    with open(CACHE_FILE, "w") as f:
                        json.dump(results, f, indent=2)
                except Exception as e:
                    print(f"Error processing row: {e}")
                
                if (i+1) % 5 == 0:
                    print(f"Processed {i+1}/{len(rows_to_process)} new rows...")

    # Final count
    print(f"Total rows evaluated: {len(results)}/{len(rows)}")

    # Now evaluate thresholds
    all_scores = [res["score"] for res in results]
    unique_scores = sorted(list(set(all_scores)))
    print(f"\nUnique scores found: {len(unique_scores)}")
    
    print("\nResults:")
    for threshold in THRESHOLDS:
        correct = 0
        total = 0
        for res in results:
            pred = decide_label(res["score"], threshold)
            if pred == res["label"]:
                correct += 1
            total += 1
        
        if total > 0:
            acc = correct / total
            print(f"Threshold {threshold} → Accuracy {acc:.2f} ({correct}/{total})")

if __name__ == "__main__":
    evaluate("data/train.csv")
