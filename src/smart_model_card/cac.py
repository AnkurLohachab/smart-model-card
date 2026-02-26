"""
Computer-Assisted Coding (CAC) helper.

Provides lightweight keyword-based code suggestions for integration into
model card tooling or data documentation workflows. This is intentionally
simple and dependency-free; replace with your NLP/coding engine as needed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class CodeSuggestion:
    code: str
    system: str
    label: str
    score: float


class ComputerAssistedCoder:
    """
    Simple keyword-based CAC engine.

    Initialize with a vocabulary mapping keywords/phrases to codes and use
    suggest_codes to retrieve ranked suggestions.
    """

    def __init__(self, vocab: Dict[str, Tuple[str, str]]):
        """
        Args:
            vocab: mapping from lowercase keyword/phrase -> (code, system)
                   e.g., {"copd": ("J44", "ICD-10"), "hypertension": ("I10", "ICD-10")}
        """
        self.vocab = {k.lower(): v for k, v in vocab.items()}

    def suggest_codes(self, text: str, top_k: int = 5) -> List[CodeSuggestion]:
        """Return ranked code suggestions based on keyword matches."""
        text_l = text.lower()
        hits: List[CodeSuggestion] = []
        for kw, (code, system) in self.vocab.items():
            if kw in text_l:
                score = len(kw) / max(len(text_l), 1)
                hits.append(CodeSuggestion(code=code, system=system, label=kw, score=score))
        hits.sort(key=lambda x: x.score, reverse=True)
        return hits[:top_k]
