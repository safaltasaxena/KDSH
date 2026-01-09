import json
import csv
import pickle
import numpy as np
import os
from src.decision import decide_label

def check_predictions():
    # We need the results from the last run. 
    # Since I don't have them saved, I'll mock the analysis or look at unique scores logic.
    
    # Let's check the labels in train.csv properly
    consistent_count = 0
    contradict_count = 0
    total = 0
    
    with open("data/train.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["label"] == "consistent":
                consistent_count += 1
            elif row["label"] == "contradict":
                contradict_count += 1
            total += 1
            
    print(f"Dataset stats: Total={total}, Consistent={consistent_count}, Contradict={contradict_count}")
    print(f"Majority Baseline: {max(consistent_count, contradict_count)/total:.2f}")

if __name__ == "__main__":
    check_predictions()
