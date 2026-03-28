import json
import re

def extract_json(text: str) -> dict:
    """
    Robustly extract JSON from LLM output.
    Handles: markdown blocks, extra text before/after, special characters.
    """
    # Step 1: strip markdown code blocks
    text = re.sub(r"```(?:json)?", "", text).strip()

    # Step 2: try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Step 3: find outermost {...} block
    try:
        start = text.index("{")
        end   = text.rindex("}") + 1
        return json.loads(text[start:end])
    except (ValueError, json.JSONDecodeError):
        pass

    # Step 4: fix common LLM JSON mistakes
    try:
        cleaned = text
        cleaned = re.sub(r",\s*}", "}", cleaned)       # trailing comma in object
        cleaned = re.sub(r",\s*]", "]", cleaned)       # trailing comma in array
        cleaned = re.sub(r"[\x00-\x1f\x7f]", " ", cleaned)  # control characters
        start = cleaned.index("{")
        end   = cleaned.rindex("}") + 1
        return json.loads(cleaned[start:end])
    except (ValueError, json.JSONDecodeError):
        pass

    return {}   # give up — caller uses fallback
