from __future__ import annotations

import json
from typing import Iterable, List

from ..schemas.commitment import Commitment, commitment_to_dict


def to_markdown(commitments: Iterable[Commitment]) -> str:
    lines: List[str] = []
    for c in commitments:
        who = c.who or "Unassigned"
        deadline = c.explicit_deadline_text or "No explicit deadline"
        lines.append(f"- **Promise**: {c.sentence}")
        lines.append(f"  - **Who**: {who}")
        lines.append(f"  - **When**: {c.created_at.isoformat()}")
        lines.append(f"  - **Deadline**: {deadline}")
        lines.append(f"  - **Status**: {c.status.value}")
        lines.append("")
    return "\n".join(lines).strip()


def to_json(commitments: Iterable[Commitment]) -> str:
    data = [commitment_to_dict(c) for c in commitments]
    return json.dumps(data, indent=2, ensure_ascii=False)


def to_table(commitments: Iterable[Commitment]) -> str:
    """
    Simple monospaced table.
    """
    rows: List[List[str]] = []
    headers = ["WHO", "PROMISE", "CREATED_AT", "DEADLINE", "STATUS"]
    rows.append(headers)

    for c in commitments:
        who = c.who or "Unassigned"
        deadline = c.explicit_deadline_text or "No explicit deadline"
        rows.append(
            [
                who,
                c.sentence,
                c.created_at.isoformat(),
                deadline,
                c.status.value,
            ]
        )

    # column widths
    col_widths = [0] * len(headers)
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    lines: List[str] = []
    for idx, row in enumerate(rows):
        padded = [
            cell.ljust(col_widths[i]) for i, cell in enumerate(row)
        ]
        lines.append(" | ".join(padded))
        if idx == 0:
            lines.append(
                "-+-".join("-" * w for w in col_widths)
            )

    return "\n".join(lines)

