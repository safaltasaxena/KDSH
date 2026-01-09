import json
from src.claim_extractor import extract_claims
from src.contradiction_logic import contradiction_score

# ---------- LOAD CONSTRAINTS (FROM DAY 2) ----------

constraints = []
with open("output/constraints.jsonl") as f:
    for line in f:
        obj = json.loads(line)
        constraints.append(obj["constraints"])

# ---------- INPUT BACKSTORY ----------

backstory = """
The character trusted authority figures deeply and believed law enforcement
would always protect him.
"""

# ---------- EXTRACT CLAIMS ----------

claims = extract_claims(backstory)

# ---------- SCORE CONTRADICTIONS ----------

total_score = 0.0

for claim in claims:
    for constraint in constraints:
        total_score += contradiction_score(claim, constraint)

# ---------- FINAL DECISION ----------

THRESHOLD = 0.5   # 👈 YOU WILL TUNE THIS

if total_score > THRESHOLD:
    print(0)   # inconsistent
else:
    print(1)   # consistent
