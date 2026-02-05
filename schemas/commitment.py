from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class CommitmentKind(str, Enum):
    PERSONAL_PROMISE = "personal_promise"
    TEAM_PROMISE = "team_promise"
    SOFT_INTENTION = "soft_intention"
    HARD_COMMITMENT = "hard_commitment"


class CommitmentStatus(str, Enum):
    PENDING = "pending"
    OVERDUE = "overdue"
    UNCLEAR = "unclear"


@dataclass
class SourceMessage:
    """Represents one message / entry in a chronological conversation."""

    text: str
    sender: Optional[str] = None
    timestamp: Optional[datetime] = None
    channel: Optional[str] = None  # e.g. "slack", "email", "github"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SentenceSpan:
    """A sentence extracted from a source message, with simple offsets."""

    text: str
    source_index: int  # index into list of SourceMessage
    char_start: int
    char_end: int


@dataclass
class Commitment:
    """Structured representation of a detected promise / commitment."""

    id: str
    sentence: str
    full_message: str
    who: Optional[str]  # "Unassigned" if unknown
    kind: Optional[CommitmentKind]
    kind_confidence: float
    created_at: datetime
    # Deadline handling: never invent – store what we know as-is.
    explicit_deadline_text: Optional[str]  # original phrase, e.g. "next week"
    explicit_deadline_date: Optional[datetime]  # only if clearly resolvable
    status: CommitmentStatus
    source: SourceMessage
    raw_llm_labels: Dict[str, Any] = field(default_factory=dict)


def commitment_to_dict(c: Commitment) -> Dict[str, Any]:
    """Safe, JSON-serialisable dict representation."""

    def _dt(d: Optional[datetime]) -> Optional[str]:
        return d.isoformat() if d else None

    data = asdict(c)
    data["kind"] = c.kind.value if c.kind else None
    data["status"] = c.status.value
    data["created_at"] = _dt(c.created_at)
    data["explicit_deadline_date"] = _dt(c.explicit_deadline_date)
    if isinstance(c.source.timestamp, datetime):
        data["source"]["timestamp"] = _dt(c.source.timestamp)
    return data

