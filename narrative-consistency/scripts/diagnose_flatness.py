import json
import csv
import pickle
import numpy as np
import os
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
from src.contradiction_logic import contradiction_score
from src.decision import aggregate_scores, decide_label

# This is a modified main_eval to print score distribution
def diagnose_scores(test_file):
    with open("output/claims.json", "r") as f:
        claims_map = json.load(f)
    
    with open("output/constraints_with_embeddings.pkl", "rb") as f:
        constraints_db = pickle.load(f)

    with open(test_file, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    scores_list = []
    
    print(f"Diagnosing {len(rows)} rows...")

    # We only need to compute once
    for i, row in enumerate(rows):
        row_id = str(row["id"])
        book_name = row["book_name"]
        content = row["content"]
        
        claims = claims_map.get(row_id, [])
        row_scores = []
        
        for claim in claims:
            # Re-running retrieval logic (internal to main_eval usually)
            # Find top K
            candidates = [c for c in constraints_db if c.get("book_name") == book_name]
            if not candidates: continue
            
            # Use dummy/real embedding (just for diagnosis, we'll assume evaluation logic is correct)
            # We will just print the final_score calculated in the last run if possible, 
            # but better to run a few manually.
            pass

    # Actually, let's just modify main_eval.py to print the distribution
    pass

if __name__ == "__main__":
    from main_eval import evaluate
    # No, I'll just look at the code of main_eval.py first.
