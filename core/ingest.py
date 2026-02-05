from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Optional, Sequence

from ..schemas.commitment import SentenceSpan, SourceMessage


@dataclass
class NormalizedConversation:
    """Canonical, sentence-level view of an input conversation."""

    messages: List[SourceMessage]
    sentences: List[SentenceSpan]


def _split_into_sentences(text: str) -> List[str]:
    """
    Very simple sentence segmentation that is good enough for
    chat/email/issues. You can swap this for spaCy or similar later.
    """
    import re

    # Split on ., ?, ! but keep them attached; also handle line breaks.
    parts = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def normalize_from_messages(
    items: Sequence[dict],
    *,
    channel: Optional[str] = None,
) -> NormalizedConversation:
    """
    Normalize a list of chronological items (e.g. chat messages, emails).

    Each item is a dict-like structure with keys:
    - "text" (required)
    - "sender" (optional)
    - "timestamp" (optional, datetime or ISO string)
    - "metadata" (optional dict)
    """
    messages: List[SourceMessage] = []
    sentences: List[SentenceSpan] = []

    for idx, raw in enumerate(items):
        text = str(raw.get("text", "")).strip()
        if not text:
            continue

        sender = raw.get("sender")
        ts = raw.get("timestamp")
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts)
            except ValueError:
                ts = None

        msg = SourceMessage(
            text=text,
            sender=sender,
            timestamp=ts,
            channel=channel or raw.get("channel"),
            metadata=raw.get("metadata") or {},
        )
        messages.append(msg)

        offset = 0
        for s in _split_into_sentences(text):
            start = text.find(s, offset)
            end = start + len(s)
            sentences.append(
                SentenceSpan(
                    text=s,
                    source_index=len(messages) - 1,
                    char_start=start,
                    char_end=end,
                )
            )
            offset = end

    return NormalizedConversation(messages=messages, sentences=sentences)


def normalize_from_text(
    text: str,
    *,
    sender: Optional[str] = None,
    timestamp: Optional[datetime] = None,
    channel: Optional[str] = None,
) -> NormalizedConversation:
    """
    Convenience wrapper for free-form text (e.g. paste-in, file).
    """
    item = {
        "text": text,
        "sender": sender,
        "timestamp": timestamp,
        "channel": channel,
    }
    return normalize_from_messages([item], channel=channel)

