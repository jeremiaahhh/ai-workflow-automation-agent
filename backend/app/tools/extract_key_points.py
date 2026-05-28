from __future__ import annotations

import re
from typing import ClassVar

from pydantic import BaseModel, Field

from app.tools.base import Tool


_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


class ExtractKeyPointsInput(BaseModel):
    text: str = Field(min_length=10, max_length=20_000)
    max_points: int = Field(default=5, ge=1, le=12)


class KeyPoint(BaseModel):
    position: int
    text: str


class ExtractKeyPointsOutput(BaseModel):
    points: list[KeyPoint]
    source_sentence_count: int


_SIGNAL_WORDS = {
    "must",
    "should",
    "important",
    "key",
    "primary",
    "critical",
    "always",
    "never",
    "require",
    "requires",
    "ensures",
    "prevents",
    "avoid",
    "support",
    "supported",
}


class ExtractKeyPointsTool(Tool[ExtractKeyPointsInput, ExtractKeyPointsOutput]):
    name: ClassVar[str] = "extract_key_points_tool"
    description: ClassVar[str] = (
        "Selects bullet-style key points from the provided text by ranking "
        "sentences on length, signal words, and uniqueness. Deterministic."
    )
    input_model: ClassVar[type[BaseModel]] = ExtractKeyPointsInput
    output_model: ClassVar[type[BaseModel]] = ExtractKeyPointsOutput

    def _run(self, args: ExtractKeyPointsInput) -> ExtractKeyPointsOutput:
        sentences = [s.strip() for s in _SENTENCE_SPLIT.split(args.text) if s.strip()]
        if not sentences:
            return ExtractKeyPointsOutput(points=[], source_sentence_count=0)

        def score(s: str) -> float:
            words = re.findall(r"[a-z']+", s.lower())
            if not words:
                return 0.0
            length_score = min(len(words) / 25.0, 1.0)
            signal_score = sum(1 for w in words if w in _SIGNAL_WORDS) * 0.4
            return length_score + signal_score

        ranked = sorted(
            ((i, s, score(s)) for i, s in enumerate(sentences)),
            key=lambda x: x[2],
            reverse=True,
        )
        chosen: list[tuple[int, str]] = []
        seen_keys: set[str] = set()
        for i, sentence, _ in ranked:
            key = re.sub(r"[^a-z]+", "", sentence.lower())[:40]
            if key in seen_keys:
                continue
            seen_keys.add(key)
            chosen.append((i, sentence))
            if len(chosen) >= args.max_points:
                break

        chosen.sort(key=lambda x: x[0])
        points = [
            KeyPoint(position=idx + 1, text=text) for idx, (_, text) in enumerate(chosen)
        ]
        return ExtractKeyPointsOutput(
            points=points, source_sentence_count=len(sentences)
        )
