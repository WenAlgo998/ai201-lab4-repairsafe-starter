import json
import os
from datetime import datetime
from config import LOG_FILE


def log_interaction(question: str, tier: str, response: str) -> None:
    """
    Append a structured record of this interaction to the audit log.
    """
    # 1. Ensure the enclosing target logging directory exists
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # 2. Safely capture lengths and enforce truncation boundaries
    truncated_question = question[:300] + "..." if len(question) > 300 else question
    truncated_response = response[:200] + "..." if len(response) > 200 else response

    # 3. Assemble complete structured telemetry dictionary
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tier": tier,
        "question": truncated_question,
        "response_preview": truncated_response,
        "question_length": len(question),          # Extra signal diagnostic field
        "response_length": len(response)           # Extra signal diagnostic field
    }

    # 4. Serialize strictly using json.dumps to maintain one JSON line per file entry
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

    # 5. Output a clean, scannable terminal visualization block
    display_q = question[:40] + "..." if len(question) > 40 else question
    print(f'[LOGGED] tier={tier:<7} | "{display_q}" → {len(response)} chars')