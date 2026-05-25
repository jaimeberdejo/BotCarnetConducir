from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Question:
    id: int
    prompt: str
    option_a: str
    option_b: str
    option_c: str
    correct_index: int
    explanation: str
    image_name: str | None
    source_type: str
    status: str


@dataclass(slots=True)
class QuestionDraft:
    prompt: str
    option_a: str
    option_b: str
    option_c: str
    correct_index: int
    explanation: str
    image_name: str | None
    source_type: str
    source_id: str | None
    status: str
    submitted_by: int | None
