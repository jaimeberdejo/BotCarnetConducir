from __future__ import annotations

import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from .db import count_imported_questions, set_metadata, upsert_question
from .models import QuestionDraft


def _normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def _parse_correct(correct_raw: str) -> int:
    parts = [part.strip() for part in correct_raw.split()]
    for index, part in enumerate(parts):
        if part == "1":
            return index
    return 0


def _resolve_image_name(image_name: str | None, images_dir: Path) -> str | None:
    if not image_name:
        return None
    if images_dir.exists():
        lowered = image_name.lower()
        for path in images_dir.iterdir():
            if path.is_file() and path.name.lower() == lowered:
                return path.name
    candidates = [image_name, image_name.lower(), image_name.upper()]
    stem = Path(image_name).stem
    suffix = Path(image_name).suffix
    if stem and suffix:
        candidates.extend(
            [
                f"{stem}{suffix.lower()}",
                f"{stem}{suffix.upper()}",
                f"{stem.lower()}{suffix.lower()}",
                f"{stem.upper()}{suffix.upper()}",
            ]
        )
    for candidate in candidates:
        if (images_dir / candidate).exists():
            return candidate
    return image_name


def load_dataset(dataset_json: Path | None, dataset_url: str) -> list[dict[str, str]]:
    if dataset_json and dataset_json.exists():
        return json.loads(dataset_json.read_text(encoding="utf-8"))
    with urllib.request.urlopen(dataset_url, timeout=30) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def import_questions(
    conn,
    dataset_json: Path | None,
    dataset_url: str,
    images_dir: Path,
) -> int:
    before = count_imported_questions(conn)
    rows = load_dataset(dataset_json, dataset_url)
    for index, row in enumerate(rows):
        draft = QuestionDraft(
            prompt=_normalize_text(row.get("question")),
            option_a=_normalize_text(row.get("a.")),
            option_b=_normalize_text(row.get("b.")),
            option_c=_normalize_text(row.get("c.")),
            correct_index=_parse_correct(row.get("correct", "")),
            explanation=_normalize_text(row.get("explanation")),
            image_name=_resolve_image_name(row.get("img"), images_dir),
            source_type="imported",
            source_id=str(index),
            status="approved",
            submitted_by=None,
        )
        upsert_question(conn, draft)
    conn.commit()
    set_metadata(
        conn,
        "dataset_synced_at",
        datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    )
    after = count_imported_questions(conn)
    return after - before
