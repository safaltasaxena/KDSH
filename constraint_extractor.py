def extract_constraints(text: str, chunk_id: int):
    """
    Input: text chunk
    Output: list of constraint dictionaries
    """

    constraints = []

    if "police" in text:
        constraints.append({
            "type": "belief",
            "entity": "MAIN_CHARACTER",
            "value": "distrusts authority",
            "confidence": 0.7,
            "chunk_id": chunk_id
        })

    if "trained in combat" in text:
        constraints.append({
            "type": "capability",
            "entity": "MAIN_CHARACTER",
            "value": "can fight",
            "confidence": 0.9,
            "chunk_id": chunk_id
        })

    if "betraying" in text:
        constraints.append({
            "type": "event",
            "entity": "MAIN_CHARACTER",
            "value": "betrayed ally",
            "confidence": 1.0,
            "chunk_id": chunk_id
        })

    return constraints
