def contradiction_score(claim, constraint):
    """
    Returns a score in [0, 1]
    0   → no contradiction
    1   → hard contradiction
    """

    # ---------- HARD CONTRADICTIONS ----------

    # 1. Irreversible event mismatch
    if constraint["type"] == "event" and claim["type"] == "event":
        if claim["value"] != constraint["value"]:
            return 1.0

    # 2. Relationship broken by irreversible event
    if constraint["type"] == "event" and claim["type"] == "relationship":
        if "loyal" in claim["value"] or "trust" in claim["value"]:
            return 1.0

    # 3. Irreversible injury contradicts physical capability
    if constraint["type"] == "event" and claim["type"] == "capability":
        injury_words = ["crippled", "paralyzed", "lost leg", "disabled"]
        if any(w in constraint["value"] for w in injury_words):
            return 1.0

    # 4. Withdrawal contradicts later active engagement
    if constraint["type"] == "event" and claim["type"] == "event":
        if "withdrew" in constraint["value"] and "organised" in claim["value"]:
            return 1.0

    # ---------- SOFT CONTRADICTIONS ----------

    # 5. Belief vs belief
    if claim["type"] == "belief" and constraint["type"] == "belief":
        if claim["value"] != constraint["value"]:
            return claim["confidence"] * constraint["confidence"]

    # 6. Capability vs capability
    if claim["type"] == "capability" and constraint["type"] == "capability":
        if claim["value"] != constraint["value"]:
            return claim["confidence"] * constraint["confidence"]

    # 7. Trait vs repeated capability
    if claim["type"] == "trait" and constraint["type"] == "capability":
        if claim["value"] != constraint["value"]:
            return 0.4 * claim["confidence"] * constraint["confidence"]

    # 8. Lifelong belief vs opposing actions
    if claim["type"] == "belief" and claim.get("scope") == "lifelong":
        if constraint["type"] == "capability":
            return 0.5 * claim["confidence"] * constraint["confidence"]

    # 9. Trait contradicts extreme moral act
    if claim["type"] == "trait" and constraint["type"] == "event":
        moral_conflicts = ["pacifist", "gentle", "merciful"]
        if any(w in claim["value"] for w in moral_conflicts):
            return 0.7 * claim["confidence"] * constraint["confidence"]
        
    # Belief vs Event (soft contradiction)
    if claim["type"] == "belief" and constraint["type"] == "event":
        if "distrust" in claim["value"] and "authority" in constraint["value"]:
           return 0.6 * claim["confidence"] * constraint["confidence"]

    # ---------- DEFAULT ----------

    return 0.0

