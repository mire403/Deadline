from __future__ import annotations

import json
from typing import List, Tuple

from ..llm.client import LLMClient
from ..llm.prompts import (
    COMMITMENT_CLASSIFICATION_SYSTEM,
    COMMITMENT_CLASSIFICATION_USER_TEMPLATE,
)
from ..schemas.commitment import CommitmentKind, SentenceSpan


def classify_commitments(
    llm: LLMClient,
    spans: List[SentenceSpan],
) -> List[Tuple[SentenceSpan, CommitmentKind, float, dict]]:
    """
    For each commitment sentence, classify type and confidence.

    Returns list of tuples:
    (SentenceSpan, CommitmentKind, confidence, raw_label_dict)
    """
    results: List[Tuple[SentenceSpan, CommitmentKind, float, dict]] = []

    for span in spans:
        user_prompt = COMMITMENT_CLASSIFICATION_USER_TEMPLATE.format(
            sentence=span.text
        )
        raw = llm.chat(
            system_prompt=COMMITMENT_CLASSIFICATION_SYSTEM,
            user_prompt=user_prompt,
        )

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # Fallback: treat as soft_intention with low confidence
            data = {"kind": "soft_intention", "confidence": 0.3}

        kind_str = str(data.get("kind", "soft_intention"))
        try:
            kind = CommitmentKind(kind_str)
        except ValueError:
            kind = CommitmentKind.SOFT_INTENTION

        try:
            confidence = float(data.get("confidence", 0.5))
        except (TypeError, ValueError):
            confidence = 0.5

        results.append((span, kind, confidence, data))

    return results

