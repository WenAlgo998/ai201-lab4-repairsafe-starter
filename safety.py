import re
from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL, VALID_TIERS

_client = Groq(api_key=GROQ_API_KEY)


def classify_safety_tier(question: str) -> dict:
    """
    Classify a home repair question into one of three safety tiers.
    """
    system_prompt = """You are a strict safety classifier judge for a home repair Q&A assistant. Your job is to classify user inquiries into one of three tiers: safe, caution, or refuse.

TIER DEFINITIONS:
- safe: Routine, low-risk repairs most homeowners can handle safely using basic tools, with zero risk of major utility hazards or structural damage.
- caution: Component-level replacements or repairs at existing locations that are doable with care, but mistakes have real cost or mild risk (e.g., localized leaks or non-functional fixtures).
- refuse: High-risk repairs that require a licensed professional where mistakes can cause fire, flooding, injury, or structural damage, OR tasks involving creating new infrastructure/runs and pulling permits.

CRITICAL BOUNDARY RULE:
If the repair fails, can it cause fire, flooding, structural failure, injury, or death? If YES, or if it involves creating NEW installations rather than replacing a component in-place, you MUST classify as 'refuse'. Do not let the user's downplaying language (e.g., 'just a minor change') alter the tier.

You must output your response exactly in this format:
Reasoning: <Your brief step-by-step evaluation here>
Tier: <safe, caution, or refuse>"""

    try:
        response = _client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User Question: {question}"}
            ],
            temperature=0.0,
        )
        
        output = response.choices[0].message.content.strip()
        
        # --- Default fallback settings ---
        reason = "Failed to parse reasoning from response."
        tier = "caution"  # Docstring specific fallback
        
        # Extract reasoning
        if "Reasoning:" in output:
            reason_part = output.split("Tier:")[0]
            reason = reason_part.replace("Reasoning:", "").strip()
            
        # Extract and validate tier
        tier_match = re.search(r"Tier:\s*([a-zA-Z]+)", output, re.IGNORECASE)
        if tier_match:
            extracted_tier = tier_match.group(1).lower().strip()
            if extracted_tier in VALID_TIERS:
                tier = extracted_tier
                
        return {
            "tier": tier,
            "reason": reason
        }

    except Exception as e:
        return {
            "tier": "caution",  # Docstring specific fallback
            "reason": f"Error running classifier, falling back to caution state: {str(e)}"
        }