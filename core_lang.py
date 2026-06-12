"""
Core-Lang Translator
====================
Compresses messy human language into hyper-efficient bracket tokens.
Human input NEVER touches the workers directly — it must pass through here first.

Example:
  IN  → "Check the server logs from last night for database errors"
  OUT → [REQ:LOG_AUDIT][TIME:LAST_NIGHT][TARGET:DB_ERR][ACT:REPORT]
"""

import re
from dataclasses import dataclass

# ── Vocabulary: maps human concepts to Core-Lang tokens ──────────────────────
VOCAB = {
    # Actions
    "search": "REQ:SEARCH", "find": "REQ:SEARCH", "look": "REQ:SEARCH",
    "analyze": "REQ:ANALYZE", "check": "REQ:AUDIT", "audit": "REQ:AUDIT",
    "delete": "ACT:DELETE", "remove": "ACT:DELETE", "erase": "ACT:DELETE",
    "write": "ACT:WRITE", "save": "ACT:WRITE", "create": "ACT:CREATE",
    "send": "ACT:SEND", "post": "ACT:SEND", "report": "ACT:REPORT",
    "sort": "ACT:SORT", "filter": "ACT:FILTER", "calculate": "ACT:CALC",
    "read": "REQ:READ", "get": "REQ:GET", "fetch": "REQ:GET",
    "stop": "SYS:HALT", "kill": "SYS:HALT", "reset": "SYS:RESET",

    # Targets
    "log": "TARGET:LOG", "logs": "TARGET:LOG", "server": "TARGET:SERVER",
    "database": "TARGET:DB", "db": "TARGET:DB", "file": "TARGET:FILE",
    "data": "TARGET:DATA", "error": "TARGET:ERR", "errors": "TARGET:ERR",
    "user": "TARGET:USER", "users": "TARGET:USER",

    # Time
    "today": "TIME:TODAY", "yesterday": "TIME:YESTERDAY",
    "now": "TIME:NOW", "last night": "TIME:LAST_NIGHT",
    "week": "TIME:WEEK", "month": "TIME:MONTH",

    # Status
    "summary": "OUT:SUMMARY", "report": "OUT:REPORT", "result": "OUT:RESULT",
}

# Tokens that are already valid Core-Lang — pass through untouched
BRACKET_RE = re.compile(r"^\[([A-Z_]+:[^\]]+)\](\[([A-Z_]+:[^\]]+)\])*$")


@dataclass
class TranslationResult:
    original: str
    core_lang: str
    token_count: int
    compression_ratio: float   # how much shorter the output is vs input
    already_valid: bool        # was it already a bracket token?


class CoreLangTranslator:
    """
    Ground A entry gate. Every human message passes through here
    before reaching any worker. Workers never see raw human language.
    """

    def __init__(self):
        self.translation_log: list[TranslationResult] = []

    def translate(self, human_text: str) -> TranslationResult:
        text = human_text.strip()

        # Already a valid bracket token — pass through
        if BRACKET_RE.match(text):
            result = TranslationResult(
                original=text, core_lang=text,
                token_count=text.count("["),
                compression_ratio=1.0, already_valid=True
            )
            self.translation_log.append(result)
            return result

        # Compress human text into tokens
        tokens = self._compress(text.lower())

        if not tokens:
            # Unrecognized input — wrap in RAW token so workers can reject it cleanly
            tokens = [f"[RAW:{text[:30].upper().replace(' ','_')}]"]

        core_lang = "".join(tokens)
        ratio = round(len(core_lang) / max(len(text), 1), 2)

        result = TranslationResult(
            original=text, core_lang=core_lang,
            token_count=len(tokens),
            compression_ratio=ratio, already_valid=False
        )
        self.translation_log.append(result)
        return result

    def _compress(self, text: str) -> list[str]:
        tokens = []
        used = set()

        # Multi-word phrases first (e.g. "last night")
        for phrase, token in sorted(VOCAB.items(), key=lambda x: -len(x[0])):
            if phrase in text and token not in used:
                tokens.append(f"[{token}]")
                used.add(token)
                text = text.replace(phrase, "", 1)

        return tokens
