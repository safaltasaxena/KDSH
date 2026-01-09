import os
from openai import OpenAI

# Initialize client globally if possible
client = None

def get_openai_client():
    global client
    if client is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            client = OpenAI(api_key=api_key)
        else:
            print("Warning: OPENAI_API_KEY not found in environment.")
    return client

def contradiction_score(claim, constraint):
    """
    Returns a score in [0, 1] using LLM-based NLI.
    0   → no contradiction / consistent / unrelated
    1   → hard contradiction
    """
    
    # Simple type check optimization to avoid calling LLM for obviously unrelated things
    # e.g. if we want to save costs. But for now, we'll try to rely on LLM.
    
    try:
        client = get_openai_client()
    except Exception as e:
        print(f"Failed to get client: {e}")
        return 0.0

    if not client:
        return 0.0

    prompt = f"""
    Context: We are checking if a hypothetical backstory contradicts the original book's narrative.
    
    Character: {constraint.get('entity', 'Unknown')}
    
    Premise (from Book): {constraint.get('value', '')} (Type: {constraint.get('type','')})
    Hypothesis (from Backstory): {claim.get('value', '')} (Type: {claim.get('type','')})

    Task: Determine if the Hypothesis contradicts the Premise for this character.
    If the Premise says X and the Hypothesis says NOT X, it is a contradiction (score 1.0).
    If they are different subjects or unrelated, it is NOT a contradiction (score 0.0).
    
    Output a single JSON object with:
    - "reasoning": "brief explanation"
    - "score": float between 0.0 (no contradiction) and 1.0 (direct contradiction).
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        import json
        content = response.choices[0].message.content
        data = json.loads(content)
        return float(data.get("score", 0.0))

    except Exception as e:
        print(f"Error in contradiction check: {e}")
        return 0.0

