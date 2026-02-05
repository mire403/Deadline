from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core.classifier import classify_commitments
from .core.detector import detect_commitment_sentences
from .core.ingest import normalize_from_messages, normalize_from_text
from .core.resolver import resolve_commitments
from .llm.client import LLMClient
from .outputs import formatter


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deadline – automatic promise / commitment detection."
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        help="Path to input text file. If omitted, read from stdin.",
    )
    parser.add_argument(
        "--format",
        "-f",
        type=str,
        default="markdown",
        choices=["markdown", "json", "table"],
        help="Output format.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    if args.input:
        text = Path(args.input).read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()

    # Normalize
    convo = normalize_from_text(text)

    # Init LLM
    llm = LLMClient()

    # Detection
    candidate_spans = detect_commitment_sentences(
        llm=llm, sentences=convo.sentences
    )

    # Classification
    classified = classify_commitments(llm=llm, spans=candidate_spans)

    # Resolution (who, deadline, status)
    commitments = resolve_commitments(
        llm=llm,
        message_index_to_source=convo.messages,
        classified_items=classified,
    )

    # Output
    if args.format == "markdown":
        out = formatter.to_markdown(commitments)
    elif args.format == "json":
        out = formatter.to_json(commitments)
    else:
        out = formatter.to_table(commitments)

    print(out)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

