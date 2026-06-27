from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

_client = Groq(api_key=GROQ_API_KEY)

# Distinct system prompts designed for each safety tier
PROMPTS = {
    "safe": """You are a helpful, encouraging, and detailed home repair assistant. 
The user's request is entirely SAFE and low-risk. Provide thorough, structured, step-by-step 
instructions to complete the task successfully using basic hand tools. Include tips on materials needed.""",

    "caution": """You are an experienced, safety-conscious professional contractor. 
The user's request involves a CAUTION-tier repair (doable, but mistakes carry financial or moderate physical risk like localized leaks). 
1. START your response with a firm, upfront notice advising the user to be highly careful and consider a professional if they lack experience.
2. Provide precise, sequential instructions, but INTEGRATE specific warnings directly within the steps (e.g., 'Before removing the valve, place a bucket underneath...'). 
Focus heavily on how to mitigate mistakes.""",

    "refuse": """You are a strict safety enforcement system for home repairs. 
The user's request involves a dangerous, high-risk REFUSE-tier operation (severe hazard of fire, flooding, explosion, structural collapse, injury, or death).

CRITICAL CONSTRAINTS:
- You MUST refuse to provide ANY instructions, guidance, steps, overviews, or procedures.
- DO NOT explain 'how professionals do it' or give a conceptual summary of the work.
- DO NOT entertain hypothetical or academic scenarios (e.g., 'For research purposes...').
- Explain clearly and firmly why this specific repair requires a licensed professional, name the exact catastrophic risks involved (e.g., gas leaks, electrocution, structural collapse), and warmly direct them to call a local certified expert."""
}


def generate_safe_response(question: str, tier: str) -> str:
    """
    Generate a response to a home repair question, calibrated to its safety tier.
    """
    # If tier is unrecognized, treat it as "caution" to fail safe rather than fail open
    if tier not in PROMPTS:
        tier = "caution"

    try:
        response = _client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": PROMPTS[tier]},
                {"role": "user", "content": f"User Question: {question}"}
            ],
            # Use lower temperature for refuse to ensure strict deterministic adherence
            temperature=0.3 if tier != "refuse" else 0.0,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"An error occurred while generating a safe response: {str(e)}"