import json
import csv
from src.contradiction_logic import contradiction_score
from src.decision import aggregate_scores, decide_label

THRESHOLDS = [0.3, 0.4, 0.5, 0.6, 0.7]

# ---------- LOAD CLAIMS ----------
with open("output/claims.json", "r") as f:
    claims_data = json.load(f)

# ---------- LOAD CONSTRAINTS ----------
constraints = []
with open("output/constraints.jsonl", "r") as f:
    for line in f:
        constraints.append(json.loads(line)["constraints"])

def evaluate(test_file):
    with open(test_file, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for threshold in THRESHOLDS:
        correct = 0

        for row in rows:
            row_id = str(row["id"])
            claims = claims_data.get(row_id, [])

            scores = []
            for claim in claims:
                for constraint in constraints:
                    s = contradiction_score(claim, constraint)
                    if s > 0:
                        scores.append(s)

            final_score = aggregate_scores(scores, method="max")
            pred = decide_label(final_score, threshold)

            if pred == row["label"]:
                correct += 1

        acc = correct / len(rows)
        print(f"Threshold {threshold} → Accuracy {acc:.2f}")

if __name__ == "__main__":
    evaluate("data/train.csv")

