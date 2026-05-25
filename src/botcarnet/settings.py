from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DATASET_URL = (
    "https://raw.githubusercontent.com/donmerendolo/"
    "anki-carnet-conducir/master/data/data_B.json"
)
IMAGE_BASE_URL = (
    "https://raw.githubusercontent.com/jaimeberdejo/"
    "botcarnet-imagenes/main/Imagenes/"
)


def load_dotenv(env_path: Path) -> None:
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


@dataclass(slots=True)
class Settings:
    bot_token: str
    db_path: Path
    images_dir: Path
    dataset_json: Path | None
    dataset_url: str
    image_base_url: str
    exam_question_count: int = 30
    exam_fail_threshold: int = 3


def get_settings() -> Settings:
    project_root = Path.cwd()
    load_dotenv(project_root / ".env")

    bot_token = os.environ.get("BOT_TOKEN", "").strip()
    if not bot_token:
        raise RuntimeError("BOT_TOKEN no configurado.")

    db_path = Path(os.environ.get("BOT_DB_PATH", project_root / "botcarnet.db"))
    images_dir = Path(os.environ.get("BOT_IMAGES_DIR", project_root / "Imagenes"))
    dataset_json_raw = os.environ.get("BOT_DATASET_JSON", "").strip()
    if dataset_json_raw:
        dataset_json = Path(dataset_json_raw)
    else:
        default_dataset = project_root / "data_B.json"
        dataset_json = default_dataset if default_dataset.exists() else None

    return Settings(
        bot_token=bot_token,
        db_path=db_path,
        images_dir=images_dir,
        dataset_json=dataset_json,
        dataset_url=os.environ.get("BOT_DATASET_URL", DATASET_URL),
        image_base_url=os.environ.get("BOT_IMAGE_BASE_URL", IMAGE_BASE_URL),
    )
