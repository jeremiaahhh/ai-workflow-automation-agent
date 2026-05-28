from __future__ import annotations

import re
from typing import ClassVar

from pydantic import BaseModel, Field

from app.tools.base import Tool


_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


class SummarizeTextInput(BaseModel):
    text: str = Field(min_length=10, max_length=20_000)
    max_sentences: int = Field(default=3, ge=1, le=10)


class SummarizeTextOutput(BaseModel):
    summary: str
    sentence_count: int
    compression_ratio: float


def _score_sentence(sentence: str, word_freq: dict[str, int]) -> float:
    words = re.findall(r"[a-z']+", sentence.lower())
    if not words:
        return 0.0
    return sum(word_freq.get(w, 0) for w in words) / len(words)


class SummarizeTextTool(Tool[SummarizeTextInput, SummarizeTextOutput]):
    name: ClassVar[str] = "summarize_text_tool"
    description: ClassVar[str] = (
        "Returns a short summary of the provided text by selecting the highest-"
        "scoring sentences (frequency-weighted, stopword-filtered). Deterministic "
        "and runs locally."
    )
    input_model: ClassVar[type[BaseModel]] = SummarizeTextInput
    output_model: ClassVar[type[BaseModel]] = SummarizeTextOutput

    _STOPWORDS: ClassVar[frozenset[str]] = frozenset(
        "the a an and or but if then so to of in on at for with as is are was "
        "were be been being this that these those it its which who whom whose "
        "from by about into over under between among not no yes do does did".split()
    )

    def _run(self, args: SummarizeTextInput) -> SummarizeTextOutput:
        sentences = [s.strip() for s in _SENTENCE_SPLIT.split(args.text) if s.strip()]
        if not sentences:
            return SummarizeTextOutput(
                summary=args.text.strip(),
                sentence_count=0,
                compression_ratio=1.0,
            )

        words = re.findall(r"[a-z']+", args.text.lower())
        freq: dict[str, int] = {}
        for w in words:
            if w in self._STOPWORDS or len(w) < 3:
                continue
            freq[w] = freq.get(w, 0) + 1

        scored = sorted(
            ((i, _score_sentence(s, freq)) for i, s in enumerate(sentences)),
            key=lambda x: x[1],
            reverse=True,
        )
        top_idxs = sorted(i for i, _ in scored[: args.max_sentences])
        summary = " ".join(sentences[i] for i in top_idxs)
        return SummarizeTextOutput(
            summary=summary,
            sentence_count=len(top_idxs),
            compression_ratio=round(len(summary) / max(len(args.text), 1), 3),
        )
