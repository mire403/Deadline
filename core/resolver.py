from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import List

from ..llm.client import LLMClient
from ..llm.prompts import (
    ATTRIBUTE_EXTRACTION_SYSTEM,
    ATTRIBUTE_EXTRACTION_USER_TEMPLATE,
)
from ..schemas.commitment import (
    Commitment,
    CommitmentKind,
    CommitmentStatus,
    SourceMessage,
)


def _extract_attributes(
    llm: LLMClient,
    sentence: str,
) -> dict:
    user_prompt = ATTRIBUTE_EXTRACTION_USER_TEMPLATE.format(sentence=sentence)
    raw = llm.chat(
        system_prompt=ATTRIBUTE_EXTRACTION_SYSTEM,
        user_prompt=user_prompt,
    )
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {"who": "Unassigned", "deadline_text": None}
    return {
        "who": data.get("who") or "Unassigned",
        "deadline_text": data.get("deadline_text"),
    }


def _compute_status(
    *,
    deadline_date: datetime | None,
    now: datetime,
) -> CommitmentStatus:
    if deadline_date is None:
        return CommitmentStatus.UNCLEAR
    return CommitmentStatus.OVERDUE if deadline_date < now else CommitmentStatus.PENDING


def resolve_commitments(
    *,
    llm: LLMClient,
    message_index_to_source: list[SourceMessage],
    classified_items: list[tuple],
    now: datetime | None = None,
) -> List[Commitment]:
    """
    Turn classified commitment sentences into fully structured commitments.

    classified_items is a list of tuples produced by classifier.classify_commitments:
      (SentenceSpan, CommitmentKind, confidence, raw_label_dict)

    Deadline policy:
    - We NEVER invent calendar dates.
    - We store the exact deadline phrase as text.
    - explicit_deadline_date is kept None for now (can be resolved later by
      a deterministic date parser if expressly desired).
    """
    now = now or datetime.utcnow()
    commitments: List[Commitment] = []

    for span, kind, confidence, raw_label in classified_items:
        attrs = _extract_attributes(llm, span.text)

        # Explicitly do NOT parse deadline_text into a concrete date here.
        deadline_text = attrs.get("deadline_text")
        deadline_date = None

        status = _compute_status(deadline_date=deadline_date, now=now)
        src = message_index_to_source[span.source_index]

        commitment = Commitment(
            id=str(uuid.uuid4()),
            sentence=span.text,
            full_message=src.text,
            who=attrs.get("who") or "Unassigned",
            kind=kind if isinstance(kind, CommitmentKind) else None,
            kind_confidence=confidence,
            created_at=src.timestamp or now,
            explicit_deadline_text=deadline_text,
            explicit_deadline_date=deadline_date,
            status=status,
            source=src,
            raw_llm_labels={"classification": raw_label, "attributes": attrs},
        )
        commitments.append(commitment)

    return commitments

