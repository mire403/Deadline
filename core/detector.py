from __future__ import annotations

from typing import List

from ..llm.client import LLMClient
from ..llm.prompts import (
    COMMITMENT_DETECTION_SYSTEM,
    COMMITMENT_DETECTION_USER_TEMPLATE,
)
from ..schemas.commitment import SentenceSpan


COMMITMENT_KEYWORDS = [
    "i will",
    "i'll",
    "we will",
    "we'll",
    "will do",
    "will fix",
    "we should",
    "i should",
    "todo",
    "later",
    "follow up",
    "follow-up",
    "get back to you",
    "take care of it",
    "address this",
]


def _keyword_prefilter(sentence: str) -> bool:
    """
    Cheap keyword gate to avoid sending obviously irrelevant sentences
    to the LLM.
    """
    lower = sentence.lower()
    return any(k in lower for k in COMMITMENT_KEYWORDS)


def detect_commitment_sentences(
    llm: LLMClient,
    sentences: List[SentenceSpan],
) -> List[SentenceSpan]:
    """
    Run sentence-level commitment detection.

    Process:
    1. Keyword prefilter for cost control.
    2. For candidate sentences, call LLM to answer YES/NO.
    """
    results: List[SentenceSpan] = []

    for span in sentences:
        if not _keyword_prefilter(span.text):
            continue

        user_prompt = COMMITMENT_DETECTION_USER_TEMPLATE.format(
            sentence=span.text
        )
        answer = llm.chat(
            system_prompt=COMMITMENT_DETECTION_SYSTEM,
            user_prompt=user_prompt,
        ).strip().upper()

        if "YES" == answer:
            results.append(span)

    return results

