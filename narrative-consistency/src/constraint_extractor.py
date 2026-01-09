import os
import json
from openai import OpenAI

# Initialize client globally if possible, or lazy load
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

def extract_constraints(text: str, chunk_id: int, book_name: str):
    """
    Input: text chunk, chunk_id, book_name
    Output: list of constraint dictionaries extracted via LLM
    """
    try:
        client = get_openai_client()
    except Exception as e:
        print(f"Failed to initialize OpenAI client: {e}")
        return []

    constraints = []

    if not client:
        return []

    # Limit text length to avoid token limits / cost, though chunks should be small
    truncated_text = text[:3000]

    prompt = f"""
    You are an expert literary analyst. 
    Analyze the following text from the book "{book_name}".
    Extract key facts, character traits, specific events, or world rules that are explicitly stated and could serve as constraints for checking narrative consistency later.
    Focus on:
    1. Characters' physical traits, internal beliefs, motivations, or past actions.
    2. Specific events that happened (e.g., "The count gave a gift to Dantes").
    3. Relationships between characters (e.g., "A is the father of B").
    4. Important nouns/locations and their states.

    Be as specific as possible. Instead of "is a person", use "is a 19-year old sailor".
    
    Return a JSON object with a key "constraints" containing a list of objects.
    Each object must have:
    - "type": one of ["belief", "capability", "event", "fact", "relationship"]
    - "entity": the subject (e.g., "Phileas Fogg", "The Count", "Edmond Dantes")
    - "value": a concise statement of the fact/trait/event (e.g., "was imprisoned in Chateau d'If", "is precise to the second")
    - "confidence": float between 0.0 and 1.0 reflecting how explicit the text is.

    Text:
    {truncated_text}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs JSON. Only output valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        content = response.choices[0].message.content
        
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            print(f"Failed to decode JSON from LLM: {content[:100]}...")
            return []
        
        for item in data.get("constraints", []):
            # Enforce schema
            if "value" in item and "type" in item:
                item["chunk_id"] = chunk_id
                item["book_name"] = book_name
                # Ensure confidence is float
                item["confidence"] = float(item.get("confidence", 0.5))
                constraints.append(item)

    except Exception as e:
        print(f"Error extracting constraints for chunk {chunk_id}: {e}")
        
    return constraints
