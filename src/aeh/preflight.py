from __future__ import annotations

import os
import shutil

KEY_VARIANTS = {
    "claude": ["ANTHROPIC_API_KEY", "CLAUDE_API_KEY"],
    "gpt": ["OPENAI_API_KEY", "OPEN_AI_API_KEY"],
    "gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_AI_API_KEY", "GOOGLE_GENAI_API_KEY"],
}


def check_claude() -> tuple[bool, str]:
    if shutil.which("claude"):
        return True, "ok"
    return False, ("error: 'claude' not found. Install the Claude Code CLI, "
                   "or try 'aeh demo' for a no-CLI walkthrough.")


def available_judges() -> tuple[list[str], list[str]]:
    present, missing = [], []
    for judge, variants in KEY_VARIANTS.items():
        (present if any(os.environ.get(v) for v in variants) else missing).append(judge)
    return present, missing
