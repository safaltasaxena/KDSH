def aggregate_scores(scores, method="max"):
    if not scores:
        return 0.0

    if method == "max":
        return max(scores)

    if method == "mean":
        return sum(scores) / len(scores)

    if method == "weighted":
        return sum(scores) / (len(scores) + 1e-6)

    return max(scores)


def decide_label(final_score, threshold):
    if final_score >= threshold:
        return "contradict"
    return "consistent"
