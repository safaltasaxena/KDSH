def aggregate_scores(scores, method="max"):
    if not scores:
        return 0.0

    if method == "max":
        return max(scores)

    if method == "mean":
        return sum(scores) / len(scores)

    if method == "weighted":
        # Implementation: Probabilistic OR (Noisy-OR)
        # This treats each score as a probability of contradiction.
        # It yields a higher score if multiple contradictions are found.
        prod = 1.0
        for s in scores:
            prod *= (1.0 - s)
        return 1.0 - prod

    # Fallback to mean (safe implementation)
    return sum(scores) / len(scores)


def decide_label(final_score, threshold):
    if final_score >= threshold:
        return "contradict"
    return "consistent"
